from __future__ import absolute_import
from . import app

app.app.run()
id_database = open("ids.db", "w")
id_database.write(
    """
{
"test": "12345"
}
"""
)
id_database.close()
