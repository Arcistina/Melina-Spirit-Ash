#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "route.h"
int main(void) {
    wchar_t buffer[128];
    MelinaString s = {0};
    assert(sizeof(s) == 40 && offsetof(MelinaString, length) == 24 && offsetof(MelinaString, capacity) == 32);
    s.text.heap = buffer; s.capacity = 127;
    wcscpy(buffer, L"menutpfbnd:/00_Solo/MENU_Knowledge_65000.tpf"); s.length = wcslen(buffer);
    assert(melina_route(&s) == 1 && !wcscmp(buffer, L"./menu/melina/large.tpf") && s.length == wcslen(buffer));
    wcscpy(buffer, L"menutpfbnd:/00_Solo/MENU_Knowledge_00113.tpf"); s.length = wcslen(buffer);
    assert(melina_route(&s) == 0 && wcsstr(buffer, L"00113"));
    wcscpy(buffer, L"menutpfbnd:/00_Solo/MENU_Knowledge_650001.tpf"); s.length = wcslen(buffer);
    assert(melina_route(&s) == 0);
    wcscpy(buffer, L"menu:/hi/SB_Icon_Melina_00.tpf"); s.length = wcslen(buffer);
    assert(melina_route(&s) == 2 && !wcscmp(buffer, L"./menu/melina/small.tpf"));
    wcscpy(buffer, L"menutpfbnd:/00_Solo/MENU_Knowledge_65000_small.tpf"); s.length = wcslen(buffer);
    assert(melina_route(&s) == 2);
    s.capacity = 10;
    assert(melina_route(&s) == 0);
    assert(melina_small_name(L"MENU_ItemIcon_65000"));
    assert(melina_small_name(L"SB_Icon_Melina_00.png"));
    assert(melina_small_name(L"Hi/MENU_Knowledge_65000_small"));
    assert(!melina_small_name(L"MENU_ItemIcon_650001"));
    assert(!melina_small_name(L"MENU_ItemIcon_00113"));
    assert(!melina_small_name(L"otherSB_Icon_Melina_00"));
    puts("ABI, native-icon passthrough, ID boundary, bounds and custom routes passed.");
    return 0;
}
