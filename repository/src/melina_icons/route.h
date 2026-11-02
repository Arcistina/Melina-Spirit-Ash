#ifndef MELINA_ROUTE_H
#define MELINA_ROUTE_H
#include <windows.h>
#include <stddef.h>
#include <string.h>
#include <wchar.h>

/* Validated prefix of the native UTF16 string. Trailing native flags are
 * intentionally neither read nor changed. This is not an owning string. */
typedef struct {
    void *allocator;
    union { wchar_t local[8]; wchar_t *heap; } text;
    size_t length;
    size_t capacity;
} MelinaString;

static wchar_t *melina_text(MelinaString *s) {
    return s->capacity < 8 ? s->text.local : s->text.heap;
}

static int melina_small_name(const wchar_t *name) {
    if (!name) return 0;
    static const wchar_t *keys[] = { L"MENU_ItemIcon_65000",
        L"SB_Icon_Melina_00", L"MENU_Knowledge_65000_small" };
    for (unsigned i=0;i<3;++i) {
        const wchar_t *p=wcsstr(name,keys[i]);
        if(p && (p==name || p[-1]==L'/')) {
            const wchar_t after=p[wcslen(keys[i])];
            if(!after || after==L'.')return 1;
        }
    }
    return 0;
}

/* Returns 1 for the large texture, 2 for the small texture, or 0 unchanged. */
static int melina_route(MelinaString *s) {
    if (!s || s->length > 512 || s->capacity < s->length || s->capacity > 65536) return 0;
    wchar_t *p = melina_text(s);
    if (!p || p[s->length] != L'\0') return 0;
    int kind = 0;
    const wchar_t *key = wcsstr(p, L"MENU_Knowledge_65000");
    if (key) {
        const wchar_t after = key[wcslen(L"MENU_Knowledge_65000")];
        if (after == L'.' || after == L'_' || after == L'\0') kind = 1;
        if (wcsstr(key, L"_small")) kind = 2;
    }
    if (wcsstr(p, L"SB_Icon_Melina_00")) kind = 2;
    if (!kind) return 0;
    const wchar_t *replacement = kind == 1
        ? L"./menu/melina/large.tpf" : L"./menu/melina/small.tpf";
    const size_t n = wcslen(replacement);
    if (n > s->capacity) return 0;
    memcpy(p, replacement, (n + 1) * sizeof(wchar_t));
    s->length = n;
    return kind;
}
#endif
