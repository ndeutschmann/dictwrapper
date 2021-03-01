from dictwrapper import NestedMapping
import pathlib

current_path = pathlib.Path(__file__).parent.absolute()

def check_dict_by_key(d,target):
    assert set(d.keys()) == set(target.keys())
    for k in d:
        assert d[k] == target[k]

class TestYAMLFileImport:
    def test_basic_dictionnary_import(self):
        nm = NestedMapping.from_yaml(current_path / "basic_dictionary.yaml")
        target = {
            'string': 'some_test',
            'integer': 3,
            'float': 3.0,
            'bool': True,
            'list': [1,2,3]
        }
        check_dict_by_key(nm, target)

    def test_tuple_import(self):
        nm = NestedMapping.from_yaml(current_path / "tuple.yaml")
        target = {
            'nice_tuple': (1,2,3)
        }

        check_dict_by_key(nm, target)

        
        # Checking type
        try:
            assert isinstance(nm['nice_tuple'], tuple)
        except AssertionError:
            import ipdb
            ipdb.set_trace

    def test_nest_dict_import_recursive(self):
        nm = NestedMapping.from_yaml(current_path / "nested_dict.yaml", recursive=True)
        target = {
            "top leaf": "top leaf label",              
            "lower leaf": "lower leaf label",
            "lowest leaf": "lowest leaf label",
            "other leaf": "other leaf label"
        }

        check_dict_by_key(nm, target)

    def test_nest_dict_import_non_recursive(self):
        nm = NestedMapping.from_yaml(current_path / "nested_dict.yaml", recursive=False)
        target = {
            "top leaf": "top leaf label",              # depth 0
            "branch": {                  # depth 0
                "lower leaf": "lower leaf label",      # depth 1
                "lower branch": {        # depth 1
                    "lowest leaf": "lowest leaf label" # depth 2 
                    } 
                },
            "other branch": {            # depth 0
                "other leaf": "other leaf label"       # depth 1
            }
        }
        check_dict_by_key(nm, target)

    



        

