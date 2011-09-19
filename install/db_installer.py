#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Module purpose
==============

Install the Domogik database based on config file values

Implements
==========


@author: Maxence Dunnewind <maxence@dunnewind.net>, Marc Schneider <marc@mirelsol.org>
@copyright: (C) 2007-2010 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import getopt, sys

from sqlalchemy import create_engine

from domogik.common import sql_schema
from domogik.common import database
from domogik.common.configloader import Loader

CURRENT_DB_VERSION_NB = "0.2.0"
__db = database.DbHelper()
__url = __db.get_url_connection_string()
__engine = create_engine(__url)

###
# Installer
###

def __drop_all_tables():
    print("Droping all existing tables...")
    # Only drop the table if it exists
    sql_schema.DeviceFeatureAssociation.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.DeviceFeature.__table__.drop(bind=__engine, checkfirst=True)    
    sql_schema.DeviceFeatureModel.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.DeviceStats.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.DeviceConfig.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.Device.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.DeviceType.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.DeviceTechnology.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.DeviceUsage.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.Room.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.Area.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.UserAccount.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.Person.__table__.drop(bind=__engine, checkfirst=True)
    # Standalone tables (no foreign keys)
    sql_schema.PluginConfig.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.SystemConfig.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.SystemInfo.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.Trigger.__table__.drop(bind=__engine, checkfirst=True)
    sql_schema.UIItemConfig.__table__.drop(bind=__engine, checkfirst=True)

def __add_initial_data():
    print("Adding initial data...")
    # Initialize default system configuration
    __db.update_system_config()
    __db.update_system_info(CURRENT_DB_VERSION_NB)

    # Create a default user account
    __db.add_default_user_account()

    # Create device usages
    __db.add_device_usage(du_id='light', du_name='Light', du_description='Lamp, light usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {&quot;step&quot;:10, &quot;unit&quot;:&quot;%&quot;}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='appliance', du_name='Appliance', du_description='Appliance usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {&quot;step&quot;:10, &quot;unit&quot;:&quot;%&quot;}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='shutter', du_name='Shutter', du_description='Shutter usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Down&quot;, &quot;state1&quot;:&quot;Up&quot;}, &quot;range&quot;: {&quot;step&quot;:10, &quot;unit&quot;:&quot;%&quot;}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='air_conditionning', du_name='Air conditioning', du_description='Air conditioning usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {&quot;step&quot;:1, &quot;unit&quot;:&quot;&amp;deg;C&quot;}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='ventilation', du_name='Ventilation', du_description='Ventilation usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {&quot;step&quot;:10, &quot;unit&quot;:&quot;%&quot;}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='heating', du_name='Heating', du_description='Heating',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {&quot;step&quot;:1, &quot;unit&quot;:&quot;&amp;deg;C&quot;}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='computer', du_name='Computer', du_description='Desktop computer usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='server', du_name='Server', du_description='Server usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='telephony', du_name='Telephony', du_description='Phone usage',
                        du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } } ')
    __db.add_device_usage(du_id='tv', du_name='TV', du_description='Television usage',
                    du_default_options='{ &quot;actuator&quot;: { &quot;binary&quot;: {&quot;state0&quot;:&quot;Off&quot;, &quot;state1&quot;:&quot;On&quot;}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} } }')
    __db.add_device_usage(du_id='water', du_name='Water', du_description='Water service',
                        du_default_options='{&quot;actuator&quot;: { &quot;binary&quot;: {}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} }}')
#    __db.add_device_usage(du_id='gas', du_name='Gas', du_description='Gas service',
#                        du_default_options='{&quot;actuator&quot;: { &quot;binary&quot;: {}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} }}')
    __db.add_device_usage(du_id='electricity', du_name='Electricity', du_description='Electricity service',
                        du_default_options='{&quot;actuator&quot;: { &quot;binary&quot;: {}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} }}')
    __db.add_device_usage(du_id='temperature', du_name='Temperature', du_description='Temperature',
                        du_default_options='{&quot;actuator&quot;: { &quot;binary&quot;: {}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {&quot;unit&quot;:&quot;&amp;deg;C&quot;}, &quot;string&quot;: {} }}')
    __db.add_device_usage(du_id='mirror', du_name='Mir:ror', du_description='Mir:ror device',
                        du_default_options='{&quot;actuator&quot;: { &quot;binary&quot;: {}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} }}')
    __db.add_device_usage(du_id='nanoztag', du_name='Nanoztag', du_description='Nanoztag device',
                        du_default_options='{&quot;actuator&quot;: { &quot;binary&quot;: {}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} }}')
    __db.add_device_usage(du_id='music', du_name='Music', du_description='Music usage',
                        du_default_options='{&quot;actuator&quot;: { &quot;binary&quot;: {}, &quot;range&quot;: {}, &quot;trigger&quot;: {}, &quot;number&quot;: {} }, &quot;sensor&quot;: {&quot;boolean&quot;: {}, &quot;number&quot;: {}, &quot;string&quot;: {} }}')

"""Upgrade process of the database

"""
def upgrade_db():
    print("Upgrading the database...")

def install_or_upgrade(create_test_db):
    """Initialize the databases (install new one or upgrade it)

    @param create_test_db : true if the test DB should be (re)created

    """
    print("Using database", __db.get_db_type())
    #TODO: improve this test
    if not sql_schema.SystemConfig.__table__.exists(bind=__engine):
        print("It appears that your database doesn't contain the required tables.")
        answer = raw_input("Should they be created? [y/N]")
        if answer != "y":
            print("Can't continue, system tables are missing")
            sys.exit(1)
        else:
            __drop_all_tables() #TODO not sure this is needed
            print("Creating all tables...")
            sql_schema.metadata.create_all(__engine)
            __add_initial_data()
    else:
        upgrade_db()

    if create_test_db:
        print("Creating test database...")
        test_url = '%s_test' % __url
        engine_test = create_engine(test_url)
        __drop_all_tables(engine_test)
        sql_schema.metadata.drop_all(engine_test)
        sql_schema.metadata.create_all(engine_test)
    print("Initialization complete.")

def usage():
    print("Usage : db_installer [-t, --test]")
    print("-t or --test : database for unit tests will created (default is False)")
    print("-r or --reset : drop all tables (default is False)")

if __name__ == "__main__":
    create_test_db = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htr", ["help", "test", "reset"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            if opt in ('-t', '--test'):
                create_test_db = True
            if opt in ('-r', '--reset'):
                answer = raw_input("Are you sure you want to drop all your tables? [y/N]")
                if answer == 'y':
                    __drop_all_tables()
                sys.exit()

    install_or_upgrade(create_test_db)