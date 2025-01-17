# QMAN [LEGACY]

## Requirements

### (a) Python

```python
import sys
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
import datetime
import Tkinter as Tk
import tkFont
import os
import fileinput
from colorama import Fore, init, Style
```

### (b) Fonts

- **Everson** (included in the `evermono.zip` archive)

## Usage

```bash
QMAN.py <ccdobs.lst> [<obj_name> -o] [<color_scheme>]
```

- **Option `<obj_name> -o`**: Count queue time for `<obj_name>`
- **Option `<color_scheme>`**: 
  - If not specified, the default color scheme is used.
  - **Possible color options**: from `cl1` to `cl14`

**Example:**

```bash
QMAN.py ccdobs.lst cl12
```

## Contents of `QMAN.tar.gz`

- `QMAN.py`
- `QMAN.pyw`
- `QMAN.ico`
- `QMAN.lnk` (for WinXP)
- `evermono.zip` ([http://www.evertype.com/emono/](http://www.evertype.com/emono/))
- `QMAN.readme` (this file)
- `ccdobs.lst` (for testing, version of 03.04.2018)

---

**Version of 11.05.2021 by:**

- **K. Kotysz**: kotysz(at)astro.uni.wroc.pl
- **P. Mikolajczyk**: mikolajczyk(at)astro.uni.wroc.pl
