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

Plugin purpose
==============

Lighting library

Implements
==========

@author: Sébastien Gallet <sgallet@gmail.com>
@copyright: (C) 2007-2009 Domogik project
@license: GPL(v3)
@organization: Domogik
"""
import traceback
from domogik.xpl.common.xplmessage import XplMessage
from domogik_packages.xpl.lib.light_scene import LightingScene

class LightingException(Exception):
    """
    lighting exception
    """

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)

class LightingAPI():
    """
    lighting API
    """

    def __init__(self, broadcast, myxpl, log, data_dir):
        """
        Init the lighting API
        @param use_cron : use of an external cron
        @param myxpl : the mysql sender
        @param log : the log facility
        """
        self.log = log
        self.broadcast = broadcast
        self.myxpl = myxpl
        self.data_files_dir = data_dir
        self._gateway = LightingGateway(broadcast, log,
            self.data_files_dir, "lighting", myxpl)

    def reload_config(self):
        '''
        Reload the configuration
        '''
        self._gateway.reload_config()

    def config_cmnd_listener(self, message):
        """
        Listen to lighting.request messages
        @param message : The XPL message
        @param myxpl : The XPL sender

         lighting.request

        This allows a sender to learn about capabilities, networks, devices and scene that can be controlled and addressed

         request=[gateinfo|netlist|netinfo|devlist|devinfo|devstate|scnlist|scninfo]
         [network=ID]
         [[device=ID]|[scene=ID]][channel=#]

        """
        self.log.debug("config_cmnd_listener : Start ...")
        commands = {
            'gateinfo': lambda x,m: self._gateway.cmnd_info(x,m),
            'register': lambda x,c,s: self._gateway.cmnd_register(x,c,s),
            'scninfo': lambda x,m: self._gateway.scenes.cmnd_scninfo(x, m),
            'scnlist': lambda x,m: self._gateway.scenes.cmnd_scnlist(x, m),
            'scnadd': lambda x,m: self._gateway.scenes.cmnd_scnadd(x, m),
            'scndel': lambda x,m: self._gateway.scenes.cmnd_scndel(x, m),
            'scnadddev': lambda x,m: self._gateway.scenes.cmnd_scnadddev(x, m),
            'scndeldev': lambda x,m: self._gateway.scenes.cmnd_scndeldev(x, m),
            'devinfo': lambda x,m: self._gateway.scenes.cmnd_devinfo(x, m),
        }
        try:
            command = None
            if 'command' in message.data:
                command = message.data['command']
            self.log.debug("config_cmnd_listener : command %s received" % (command))
            network = None
            if 'network' in message.data:
                network = message.data['network']
            if self._gateway.accept_network(network):
                commands[command](self.myxpl, message)
            else:
                self.log.info("config_cmnd_listener : Message to network %s refused by the filter" % (network))
        except:
            error = "Exception : %s" %  \
                     (traceback.format_exc())
            self.log.error("config_cmnd_listener : "+error)

    def basic_cmnd_listener(self, message):
        """
        """
        self.log.debug("basic_cmnd_listener : Start ...")
        commands = {
            'register': lambda x,c,s: self._gateway.cmnd_register(x,c,s),
        }
        #These commands are generated by our devices.
        #We don't need to manage them
        badcommands = ["activate", "deactivate"]
        try:
            command = None
            if 'command' in message.data:
                command = message.data['command']
            if command not in badcommands :
                self.log.debug("basic_cmnd_listener : command %s received" % (command))
                network = None
                if 'network' in message.data:
                    network = message.data['network']
                if self._gateway.accept_network(network):
                    commands[command](self.myxpl, command, message)
                else:
                    self.log.info("basic_cmnd_listener : Message to network %s refused by the filter" % (network))
        except:
            error = "Exception : %s" %  \
                     (traceback.format_exc())
            self.log.error("basic_cmnd_listener : "+error)

    def basic_trig_listener(self, message):
        """
        """
        self.log.debug("basic_trig_listener : Start ...")
        badcommands = ["activate", "deactivate", 'scninfo', 'scnlist', \
            'scnadd', 'scndel', 'scnadddev', 'scndeldev', 'gateinfo' ]
        try:
            sensor = None
            if "device" in message.data:
                sensor = message.data["device"]
        except:
            error = "Exception : %s" %  \
                     (traceback.format_exc())
            self.log.error("basic_trig_listener : "+error)

class LightingGateway():
    """
    This describes the software that sits on the xPL network and
    is attached to an HA protocol interface (i.e. a CM11 for X10,
    PIM for UPB, etc). It sends and receives xPL messages and
    translates them to/from the underlying HA protocol. Depending on
    the abilities of the underlying HA protocol, it may be a very
    thin layer (translating literally from one format to another with
    no other processing) or thicker (taking more abstract commands
    from xPL and possibly turning them into multiple HA protocol
    commands, caching and tracking device state, etc).

    The gateway may represent a central hvac control panel or thermostat,
    but it is equally possible for it to be just a pathway
    to a collection of sensors. For example, a PC RF receiver
    could implement the hvac schema for sending events received
    from temperature sensors, without any heating or cooling setpoints
    being defined. In this case, each sensor would be assigned
    to a zone and would just send state change triggers to the xPL
    world when the temperature changed. Another hvac gateway or
    an xPLHal style program could then act on these messages.
    """

    def __init__(self, broadcast, log, data_dir, name, myxpl):
        """
        Initialiez the class
        """
        self.broadcast = broadcast
        self._protocol = "VIRTUAL"
        self._description = "Domogik Lighting Gateway"
        self._version = "0.0.1"
        self._author = "Domogik Team"
        self._info_url = "http://www.domogik.org/"
        self.data_files_dir = data_dir
        self.name = name
        self.myxpl = myxpl
        self.log = log
        self.preferred_network = "n0"
        self.scenes = LightingScene(self, self.data_files_dir)
        self.clients = LightingClient(self, self.data_files_dir)

    def reload_config(self):
        '''
        Reload configuration
        '''
        self.scenes.reload_config()

    def status(self):
        """
        Return status of the gateway
        """
        return True

    def accept_network(self, network):
        """
        Let you to filter the network.
        If broadcast is enable, the gateway dispatch the message to all zones,
        even those that are not managed by him self.
        If not only the messages for configured zones are displayed.
        broadcast should be enabled on core manager gateway.
        broadcast should be disabled on thermostats, heaters, ...,
        """
        if self.broadcast:
            return True
        elif network == None:
            return True
        elif network == self.preferred_network:
            return True
        else:
            return False

    def cmnd_info(self, myxpl, message):
        """
        """
        self.sendxpl_info(myxpl, "xpl-stat")

    def trig_info(self, myxpl, message):
        """
        """
        self.sendxpl_info(myxpl, "xpl-trig")

    def sendxpl_info(self, myxpl, xpltype):
        """
        @param myxpl : The XPL sender
        @param message : The XPL message

        This allows a sender to learn about capabilities, networks,
        devices and scene that can be controlled and addressed
        request=[gateinfo|netlist|netinfo|devlist|devinfo|devstate|scnlist|scninfo]
        [network=ID]
        [[device=ID]|[scene=ID]][channel=#]

        Provides basic information about the gateway

        lighting.gateinfo
         status=ok
         protocol=[X10|UPB|CBUS|ZWAVE|INSTEON]
         description=
         version=
         author=
         info-url=
         net-count=#
         preferred-net=ID
         scenes-ok=[true|false]
         channels-ok=[true|false]
         fade-rate-ok=[true|false]
         [fade-rate-list=#[,#....]]

        status=ok
        Status is always OK since there are no possible invalid parameters for the request.
        protocol=
        A very short, mnemonic name for the underlying HA protocol this gateway is talking to. If you have a new protocol not listed, please send a note and we'll add it to the list (keep the name short (1-8 characters), with no spaces and in upper case)
        NOTE: This is informational ONLY - a client should not tailor it's interaction with the gateway based on this. If you ever find that necessary, the underlying gateway is broken and needs to be fixed by it's author.
        description=
        Summary description of this gateway. Something in simple but helpful to an end user like "xPL to UPB PIM-based gateway".
        version=
        Version of this gateway. This should be a "raw" version number (that is, it should not be proceeded with a V or a Version or anything -- V1.0 is NOT valid, 1.0 would be). There is no structure otherwise imposed on this version as it should be informational only.
        author=
        Name of the author (company or person) of this gateway.
        info-url=
        URL of a website where more information about the gateway can be found.
        net-count=#
        Number of networks available to this gateway (will be 1 almost all the time).
        NOTE: This will never be 0. There is ALWAYS at least one network, even for HA protocols that do not have the concept of "network"s.
        preferred-net=ID
        The network ID number of the preferred (or default) network for this gateway. All commands that arrive without an explicit network= entry will be applied to this network.
        scenes-ok=[true|false]
        If the underlying HA protocol does not support scenes and the xPL gateway does not support scenes, this will be no. If the HA protocol supports scenes OR the xPL gateway has implemented "virtual" scenes, then the value is true
        NOTE: Treat this as a HINT only!
        Even if a gateway says it does not support scenes, it must reply correctly to a scnlist (with and empty list) as well as provide suitable values in the netinfo and devinfo messages for scene count (i.e. scene-count=0).
        channels-ok=[true|false]
        Indicates if the underlying HA protocol supports the idea of multiple channels on devices. If so, this is true. If not, this is false.
        NOTE: Even if channels are not supported by the underlying hardware, all controllable devices should report having one channel and that one channel also being the primary channel. Only non-controllable devices (like some keypad controllers) should ever report having no channels.
        NOTE: Treat this as a HINT only!
        Even if the gateway says it does not support channels, all channel related items described in this schema still must be supplied and supported. In such cases, the gateway should make sure all devices described support a single channel and send reports/triggers out exactly as if the protocol DID support multi-channel devices and you were describing a device that supported only one channel.
        fade-rate-ok=[true|false]
        Indicates if the underlying HA protocol supports the idea of setting the rate a change to a devices level should take place. If a fade rate can be sent along with a command to change a devices level, then this should be true. If the protocol cannot be used and will be ignored, then return false.
        NOTE: Treat this as a HINT only!
        Even if a gateway/protocol does not support fade rates, they still be specified where required (many places, fade rates are optional can be omitted). The gateway must accept a fade rate on appropriate commands, though it will probably just ignore it when processing the rest of the command.
        fade-rate-list=#[,#[,#...]]
        Optional. If the gateway supports fade rates and has a fixed, predetermined list of valid fade rates, it can enumerate them here. The rates are in seconds and can have decimals (i.e. 0,3.3,5,6.6). Rates must be ordered from lowest to highest (in terms of time) and like all lists in the lighting schema, there can be only numbers and commas (no white space). The "default" fade rate is NEVER included in this list (only numerics).
        Even if a fade-rate-list= is provided, the gateway should still accept ANY valid number as a fade-rate (if it supports fade-rates) and convert it to the nearest valid fade rate.
        This list is optional. If the gateway cannot determine the list or the underlying protocol doesn't support fade rates OR allows *any* # of seconds as a fade rate (making a list of discreet values meaningless), then it can be omitted. This list can be valuable to user interfaces in presenting a list of known rates to a user, so if at all possible, the gateway author should try to include them         }
        """
        mess = XplMessage()
        mess.set_type(xpltype)
        mess.set_schema("lighting.config")
        mess.add_data({"command" : "gateinfo"})
        mess.add_data({"status" : self.status()})
        mess.add_data({"protocol" : self._protocol})
        mess.add_data({"description" : self._description})
        mess.add_data({"version" :  self._version})
        mess.add_data({"author" : self._author})
        mess.add_data({"info-url" : self._info_url})
        mess.add_data({"net-count" : self.net_count()})
        mess.add_data({"preferred-net" : self.preferred_network})
        mess.add_data({"scenes-ok" : "true"})
        mess.add_data({"channels-ok" : "false"})
        mess.add_data({"fade-rate-ok" : "false"})
        myxpl.send(mess)

    def net_count(self):
        """
        """
        return 1

    def cmnd_register(self, myxpl, command, message):
        """
        Register a client
        command=register
        client=name
        activate=activate
        deactivate=deactivate
        """
        mess = XplMessage()
        mess.set_type("xpl-trig")
        mess.set_schema("lighting.config")
        mess.add_data({"command" : command})
        client = None
        if 'client' in message.data:
            client = message.data['client']
        activate = None
        if 'activate' in message.data:
            activate = message.data['activate']
        deactivate = None
        if 'deactivate' in message.data:
            deactivate = message.data['deactivate']
        if client == None:
            self.log.error("Command = %s : Missing parameter _ client _." % (command))
            mess.add_data({"error" : "Missing parameter : client"})
        elif not self.clients.is_valid(client):
            mess.add_data({"client" : client})
            mess.add_data({"error" : "Client already registered : %s" % client})
            self.log.error("Command = %s : Client _ %s _ already registered." % (command, client))
        else:
            self.clients.add_client(client, activate, deactivate)
            mess.add_data({"client" : client})
        myxpl.send(mess)

class LightingClient():
    """
    Manage the clients of the lighting plugin.
    A client can be a plugin or an external (arduino)
    """
    def __init__(self, gateway, data_dir):
        """
        Initialise the class.
        """
        self._data_files_dir = data_dir
        self._clients = {}

    def add_client(self, client, cmnd_activate=None, cmnd_deactivate=None):
        """
        Add a new client to manager.
        """
        if not self.is_valid(client):
            if cmnd_activate == None :
                cmnd_activate = "activate"
            if cmnd_deactivate == None :
                cmnd_deactivate = "deactivate"
            self._clients[client] = {"cmnd_activate" : cmnd_activate,
                                     "cmnd_deactivate" : cmnd_deactivate}
            return True
        else:
            return False

    def del_client(self, client):
        """
        Delete a client from manager.
        """
        if self.is_valid(client):
            del (self._clients[client])
            return True
        else:
            return False

    def is_valid(self, client):
        """
        Return True if the client is managed.
        """
        return client != None and client in self._clients

    def count(self):
        """
        Return the number of clients.
        """
        return len(self._clients)
