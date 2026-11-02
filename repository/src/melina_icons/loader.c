/* Melina Icons. Native hook uses MinHook, see its bundled third-party license. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>
#include "MinHook.h"
#include "route.h"

static HMODULE self_module;
static wchar_t log_path[32768];
static SRWLOCK log_lock = SRWLOCK_INIT;
static volatile LONG diagnostic_count;
typedef void *(__fastcall *FormatFn)(void *, MelinaString *, MelinaString *);
static FormatFn original_format;

static void log_line(const char *line) {
    if (!log_path[0]) return;
    AcquireSRWLockExclusive(&log_lock);
    HANDLE f = CreateFileW(log_path, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f != INVALID_HANDLE_VALUE) {
        DWORD count;
        WriteFile(f, line, (DWORD)strlen(line), &count, NULL);
        WriteFile(f, "\r\n", 2, &count, NULL);
        CloseHandle(f);
    }
    ReleaseSRWLockExclusive(&log_lock);
}

static int readable(const void *p, size_t size) {
    MEMORY_BASIC_INFORMATION b;
    if (!p || !VirtualQuery(p, &b, sizeof(b)) || b.State != MEM_COMMIT ||
        (b.Protect & (PAGE_GUARD | PAGE_NOACCESS))) return 0;
    return (uintptr_t)p + size >= (uintptr_t)p &&
        (uintptr_t)p + size <= (uintptr_t)b.BaseAddress + b.RegionSize;
}

#include "native_small.h"

static void * __fastcall format_hook(void *owner, MelinaString *out, MelinaString *in) {
    void *result = original_format(owner, out, in);
    if (!readable(out, sizeof(*out)) || out->length > 512 || out->capacity > 65536 ||
        out->length > out->capacity) return result;
    wchar_t *p = melina_text(out);
    if (!readable(p, (out->length + 1) * sizeof(wchar_t)) || p[out->length] != L'\0') return result;
    if (wcsstr(p, L"65000") || wcsstr(p, L"Melina")) {
        char before[2048] = {0}, line[2200];
        WideCharToMultiByte(CP_UTF8, 0, p, -1, before, sizeof(before), NULL, NULL);
        const int kind = melina_route(out);
        if (InterlockedIncrement(&diagnostic_count) <= 64) {
            snprintf(line, sizeof(line), "custom URI kind=%d original=%s", kind, before);
            log_line(line);
        }
    }
    return result;
}

static int executable_hash(const wchar_t *path, char hex[65]) {
    BCRYPT_ALG_HANDLE alg = NULL;
    BCRYPT_HASH_HANDLE hash = NULL;
    HANDLE f = INVALID_HANDLE_VALUE;
    BYTE digest[32], *buffer = NULL;
    int ok = 0;
    if (BCryptOpenAlgorithmProvider(&alg, BCRYPT_SHA256_ALGORITHM, NULL, 0) < 0) goto done;
    if (BCryptCreateHash(alg, &hash, NULL, 0, NULL, 0, 0) < 0) goto done;
    f = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f == INVALID_HANDLE_VALUE) goto done;
    buffer = HeapAlloc(GetProcessHeap(), 0, 1024 * 1024);
    if (!buffer) goto done;
    DWORD n;
    for (;;) {
        if (!ReadFile(f, buffer, 1024 * 1024, &n, NULL)) goto done;
        if (!n) break;
        if (BCryptHashData(hash, buffer, n, 0) < 0) goto done;
    }
    if (BCryptFinishHash(hash, digest, sizeof(digest), 0) < 0) goto done;
    for (unsigned i = 0; i < 32; ++i) sprintf(hex + i * 2, "%02x", digest[i]);
    hex[64] = '\0';
    ok = 1;
done:
    if (buffer) HeapFree(GetProcessHeap(), 0, buffer);
    if (f != INVALID_HANDLE_VALUE) CloseHandle(f);
    if (hash) BCryptDestroyHash(hash);
    if (alg) BCryptCloseAlgorithmProvider(alg, 0);
    return ok;
}

static DWORD WINAPI initialize(void *unused) {
    (void)unused;
    wchar_t exe[32768], module[32768];
    if (!GetModuleFileNameW(NULL, exe, 32768) || !GetModuleFileNameW(self_module, module, 32768)) return 0;
    const wchar_t *name = wcsrchr(exe, L'\\');
    if (!name || _wcsicmp(name + 1, L"eldenring.exe")) return 0;
    wchar_t *last = wcsrchr(module, L'\\');
    if (!last) return 0;
    *last = L'\0';
    /* The helper must live outside Game. Never write a log in the game folder. */
    const size_t game_dir_length = (size_t)(name - exe);
    if (!_wcsnicmp(module, exe, game_dir_length) &&
        (module[game_dir_length] == L'\0' || module[game_dir_length] == L'\\')) return 0;
    if (wcslen(module) + 20 >= 32768) return 0;
    swprintf(log_path, 32768, L"%ls\\MelinaIcons.log", module);
    log_line("MelinaIcons probe 0.2; custom-only image routing and native small-image registration");
    char hash[65];
    if (!executable_hash(exe, hash) || strcmp(hash,
        "f9118fea2cfd8fa3901e8060bfadb1552cb2471771ded8a5b662c4e298ffb328")) {
        log_line("Unsupported executable: no hook installed.");
        return 0;
    }
    unsigned char *base = (unsigned char *)GetModuleHandleW(NULL);
    const IMAGE_DOS_HEADER *dos = (const IMAGE_DOS_HEADER *)base;
    const IMAGE_NT_HEADERS64 *nt = (const IMAGE_NT_HEADERS64 *)(base + dos->e_lfanew);
    if (dos->e_magic != IMAGE_DOS_SIGNATURE || nt->Signature != IMAGE_NT_SIGNATURE ||
        nt->FileHeader.Machine != IMAGE_FILE_MACHINE_AMD64 || nt->OptionalHeader.SizeOfImage < 0xd7f22a) return 0;
    static const unsigned char expected[] = {
        0x40,0x55,0x56,0x57,0x48,0x8b,0xec,0x48,0x83,0xec,0x70,0x48,
        0xc7,0x45,0xb8,0xfe,0xff,0xff,0xff,0x48,0x89,0x9c,0x24,0x90
    };
    void *target = base + 0xd7efb0;
    if (memcmp(target, expected, sizeof(expected))) {
        log_line("URI formatter signature mismatch: no hook installed.");
        return 0;
    }
    game_base=base;
    if(!image_abi_valid(base)) {
        log_line("Native image ABI mismatch: no hooks installed.");return 0;
    }
    if (MH_Initialize() != MH_OK ||
        MH_CreateHook(target, format_hook, (void **)&original_format) != MH_OK ||
        MH_CreateHook(base+NATIVE_TEXTURE_LOOKUP,texture_lookup_hook,(void**)&original_texture_lookup)!=MH_OK ||
        MH_QueueEnableHook(target)!=MH_OK ||
        MH_QueueEnableHook(base+NATIVE_TEXTURE_LOOKUP)!=MH_OK ||
        MH_ApplyQueued()!=MH_OK) {
        log_line("Hook installation failed.");
        return 0;
    }
    HMODULE pinned;
    GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_PIN,
        (LPCWSTR)(uintptr_t)&initialize, &pinned);
    log_line("URI formatter hook installed; all other identifiers use original behavior.");
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        self_module = instance;
        DisableThreadLibraryCalls(instance);
        HANDLE thread = CreateThread(NULL, 0, initialize, NULL, 0, NULL);
        if (thread) CloseHandle(thread);
    }
    return TRUE;
}
