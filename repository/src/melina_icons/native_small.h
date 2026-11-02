/* Native ABI/ownership sequence researched in Flammrock/ERNativeUI (MIT).
 * See the bundled ERNativeUI third-party notice. No framework DLL is needed.
 * Only a process-lifetime image for Melina's small icon is constructed here. */
#include "native_272.h"
typedef struct { unsigned width, height; } SmallImageSize;
typedef struct { unsigned width, height; size_t pitch, bytes; unsigned char *data; } SmallImagePlane;
typedef struct {
    unsigned format, use;
    unsigned char flags, levels;
    unsigned short count;
    unsigned padding;
    SmallImagePlane *planes;
    void *palette;
    SmallImagePlane plane;
} SmallImageData;
typedef void *(*SmallCreateFn)(unsigned,unsigned,const SmallImageSize*,unsigned,void*,void*);
typedef unsigned char (*SmallGetDataFn)(void*,SmallImageData*);
typedef void (*SmallClearFn)(SmallImageData*);
typedef void *(*SmallAllocFn)(void*,size_t,void*);
typedef void *(*SmallResourceCtorFn)(void*,const wchar_t*,void*,unsigned);
typedef void (*SmallAddRefFn)(void*);
typedef void **(*TextureLookupFn)(void*,void**,const wchar_t*);
static TextureLookupFn original_texture_lookup;
static unsigned char *game_base;
static void *small_resource, *small_image;
static int small_attempted;
static SRWLOCK small_lock = SRWLOCK_INIT;

static int image_abi_valid(unsigned char *b) {
    return !memcmp(b+NATIVE_TEXTURE_LOOKUP,sig_texture_lookup,16) &&
        !memcmp(b+NATIVE_RAW_IMAGE_CREATE,sig_raw_image_create,16) &&
        !memcmp(b+NATIVE_RAW_IMAGE_GET_DATA,sig_raw_image_get_data,16) &&
        !memcmp(b+NATIVE_IMAGE_DATA_CLEAR,sig_image_data_clear,16) &&
        !memcmp(b+NATIVE_IMAGE_RESOURCE_CONSTRUCTOR,sig_image_resource_constructor,16) &&
        !memcmp(b+NATIVE_IMAGE_RESOURCE_ADD_REF,sig_image_resource_add_ref,16);
}

static void prepare_small_image(void) {
    small_attempted = 1;
    wchar_t path[32768];
    DWORD length=GetModuleFileNameW(self_module,path,32768);
    if (!length || length>32700) return;
    wchar_t *last=wcsrchr(path,L'\\'); if(!last)return;
    wcscpy(last,L"\\menu\\melina\\small.rgba");
    HANDLE file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(file==INVALID_HANDLE_VALUE){log_line("small: pixel asset missing");return;}
    LARGE_INTEGER size; unsigned char *pixels=NULL; DWORD got=0;
    if(GetFileSizeEx(file,&size) && size.QuadPart==160*160*4) {
        pixels=HeapAlloc(GetProcessHeap(),0,160*160*4);
        if(pixels && (!ReadFile(file,pixels,160*160*4,&got,NULL) || got!=160*160*4)) {
            HeapFree(GetProcessHeap(),0,pixels);pixels=NULL;
        }
    }
    CloseHandle(file);
    if(!pixels){log_line("small: invalid pixel asset");return;}
    SmallImageSize dimensions={160,160};
    void *image=((SmallCreateFn)(game_base+NATIVE_RAW_IMAGE_CREATE))(1,1,&dimensions,0,NULL,NULL);
    if(!readable(image,16) || *(void**)image != game_base+NATIVE_RAW_IMAGE_VTABLE) {
        HeapFree(GetProcessHeap(),0,pixels);log_line("small: image identity failed");return;
    }
    SmallImageData view={0};view.count=1;view.planes=&view.plane;
    int valid=((SmallGetDataFn)(game_base+NATIVE_RAW_IMAGE_GET_DATA))(image,&view);
    valid=valid && view.format==1 && view.use==0 && view.levels==1 && view.count==1 &&
        view.planes==&view.plane && view.plane.width==160 && view.plane.height==160 &&
        view.plane.pitch>=640 && view.plane.pitch<=8192 &&
        view.plane.bytes>=view.plane.pitch*160 && readable(view.plane.data,view.plane.pitch*160);
    if(valid)for(unsigned y=0;y<160;++y)memcpy(view.plane.data+y*view.plane.pitch,pixels+y*640,640);
    HeapFree(GetProcessHeap(),0,pixels);
    ((SmallClearFn)(game_base+NATIVE_IMAGE_DATA_CLEAR))(&view);
    if(!valid){log_line("small: native pixel-plane validation failed");return;}
    void *heap=*(void**)(game_base+NATIVE_SCALEFORM_GLOBAL_HEAP);
    if(!readable(heap,sizeof(void*)) || !readable(*(void**)heap,0x58)) {
        log_line("small: native heap unavailable");return;
    }
    SmallAllocFn alloc=*(SmallAllocFn*)((unsigned char*)*(void**)heap+0x50);
    void *storage=alloc(heap,0x98,NULL);
    if(!storage){log_line("small: native allocation failed");return;}
    void *resource=((SmallResourceCtorFn)(game_base+NATIVE_IMAGE_RESOURCE_CONSTRUCTOR))(
        storage,L"SB_Icon_Melina_00",image,1);
    if(!readable(resource,0x20) || *(void**)((unsigned char*)resource+0x18)!=image) {
        log_line("small: resource identity failed");return;
    }
    /* Keep one root for both allocations until process exit. Each lookup
       receives exactly one extra owned reference, like the native function. */
    small_image=image;small_resource=resource;
    log_line("small: native RGBA image and resource registered (160x160)");
}

static void **texture_lookup_hook(void *repository,void **out,const wchar_t *name) {
    if(name && readable(name,2) && (wcsstr(name,L"65000") || wcsstr(name,L"Melina"))) {
        char text[1024]={0},line[1100];
        WideCharToMultiByte(CP_UTF8,0,name,-1,text,sizeof(text),NULL,NULL);
        if(InterlockedIncrement(&diagnostic_count)<=64) {
            snprintf(line,sizeof(line),"custom texture lookup name=%s",text);log_line(line);
        }
    }
    if(!name || !readable(name,2) || !melina_small_name(name))return original_texture_lookup(repository,out,name);
    if(!out || !readable(out,sizeof(void*)))return original_texture_lookup(repository,out,name);
    AcquireSRWLockExclusive(&small_lock);
    if(!small_attempted)prepare_small_image();
    void *resource=small_resource;
    if(resource)((SmallAddRefFn)(game_base+NATIVE_IMAGE_RESOURCE_ADD_REF))(resource);
    ReleaseSRWLockExclusive(&small_lock);
    if(!resource)return original_texture_lookup(repository,out,name);
    *out=resource;return out;
}
