{ python3Packages, pythonDeps }:
python3Packages.buildPythonApplication {
	pname = "offtoot";
	version = "0.1";
	format = "pyproject";

	propagatedBuildInputs = pythonDeps python3Packages;

	src = ./.;
}
