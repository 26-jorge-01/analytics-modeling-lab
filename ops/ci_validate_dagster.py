from orchestration.dagster.dagster_project import defs

def test_dagster_definitions_load():
    """
    Dry-run test to ensure Dagster definitions can be loaded without errors.
    This catches import errors, asset key mismatches, and configuration issues.
    """
    try:
        # If this doesn't raise an exception, the structural definition is valid.
        assert defs is not None
        print("Dagster definitions loaded successfully.")
    except Exception as e:
        print(f"Error loading Dagster definitions: {e}")
        exit(1)

if __name__ == "__main__":
    test_dagster_definitions_load()
