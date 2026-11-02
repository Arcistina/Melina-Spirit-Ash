# Rebuilding the icon helper

The shipped helper was built with Zig 0.13.0 for x86_64-windows-gnu and MinHook v1.3.4 (commit c3fcafdc10146beb5919319d0683e44e3c30d537).

Place the included MinHook source under third_party/minhook and run build_windows.ps1 with Zig on PATH (or pass -Zig). It builds/runs the URI/identifier/bounds contract test, then creates out/MelinaIcons.dll. No game files are modified or required to compile.

route.h accesses only the allocator/buffer/length/capacity prefix of a native string. Native flags beyond that prefix are left untouched. native_272.h is an exact executable profile, not a cross-version API. Do not update a version label or bypass the hash/interface checks to claim support for another game build. New native coordinates require independent ABI and runtime validation.

The small image is read from menu/melina/small.rgba beside the module: exactly 160x160 row-major RGBA bytes, derived from the approved premultiplied icon. Native image-resource ownership follows the retained-root / owned-lookup-reference contract researched in ERNativeUI. Only this mod's private small-icon names are intercepted; other resource names use the original function.

The large image is supplied as menu/melina/large.tpf.dcx. The native URI formatter is redirected only for MENU_Knowledge_65000. The game's normal file loader adds .dcx and ModEngine2 resolves the mod file. Native image archives and placeholder images stay in the original game.

Third-party notices are included under LICENSES in the distribution. No ERNativeUI host DLL is required. The compiler and build caches are not distributed. Rebuilt binaries must be tested against their intended executable; this source is not a guarantee that an arbitrary compiler/build combination has been runtime-accepted.
