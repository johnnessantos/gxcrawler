
# [Configure virtual environment](#create-virtual-env)
In CMD run this command lines:
```bash
python -m venv env
gxcrawlervenv\Scripts\activate
pip install -r requirements.txt
```

# [Generate dabatase](#generate-database-sqlite)
The database used to store the search results was sqlite. Therefore, it is necessary to create the structure for storage that can be performed by the commands:
```bash
python gxcrawler/database.py
```

# Getting Started
Using enviroment variables Windows in CMD execute this commands lines:
```bash
set GX_USER=user
set GX_PASSWORD=password
set GX_URL=url
set GX_KBNAME=kbname
```
Or use file of configuration in .\gxcrawler\\.env with the lines:
```
GX_USER=user
GX_PASSWORD=password
GX_URL=url
GX_KBNAME=kbname
```

With python installed, run this command for your API to run, the result will be in the project directory with the name of database.db being from the sqlite database. ([Virtual environments](#create-virtual-env) recommended):

```python
import datetime

from process import Process

process = Process()
date = datetime.datetime(2020, 11, 1, 0, 0, 0, 0)
while date <= datetime.datetime.today():
    process.capture_data(date, date)
    date += datetime.timedelta(days=1)

```
<span style='color:red'>Attention</span>: Be careful to make this available in code repositories like gitlab or github add it to .gitignore

