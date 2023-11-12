{
  description = "Offline mastodon reader";

  inputs = {
		nixpkgs.url = "nixpkgs/nixos-unstable";
		flake-utils.url = "github:numtide/flake-utils";
	};

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let 
				pkgs = nixpkgs.legacyPackages.${system}; 
				pythonDeps = p: with p; [ mastodon-py hatchling dataclasses-json ];
			in {
        packages = rec {
          offtoot = pkgs.callPackage ./package.nix { inherit pythonDeps; };
          default = offtoot;
        };
        apps = rec {
          offtoot = flake-utils.lib.mkApp { drv = self.packages.${system}.offtoot; };
          default = offtoot;
        };
				devShells = rec {
					offtoot = pkgs.mkShell {
						buildInputs = [ (pkgs.python3.withPackages pythonDeps) ];
					};
					default = offtoot;
				};
      }
    );
}
