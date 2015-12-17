# Reloadr

Python hot code reloading tool.

`pip install reloadr`

# Usage

You can simply decorate your functions / classes with `@reloadr` and you are ready to go.

```python
from reloadr import reloadr

@reloadr
def do_something(a, b):
    return a + b

@reloadr
class SomeThing:
    def do_stuff(self):
        pass
```
