{ pkgs ? import <nixpkgs> {} }:
with pkgs;
(import ./default.nix {}).overrideAttrs (self: {
  nativeBuildInputs = self.nativeBuildInputs ++ [ cachix jq ];
  preShellHook = ''
    cachix use ${self.pname}
    ${self.preShellHook}
  '';
})
