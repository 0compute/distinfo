{ pkgs ? import <nixpkgs> {} }:
with pkgs;
(import ./default.nix {}).overrideAttrs (old: {
  nativeBuildInputs = old.nativeBuildInputs ++ [ cachix jq ];
})
