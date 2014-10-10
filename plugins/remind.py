import time
import datetime
import humanize
import parsedatetime

from modules import util
from collections import defaultdict

reminders = defaultdict(list)
pdt = parsedatetime.Calendar()

def init ():
    reminders = data_writer.get("reminders.db")

def client_connected (client):
    reminders[client.server][:] = [r for r in reminders[client.server] if schedule_reminder(client, r)]
    save(client)

def save (client):
    data_writer.add("reminders.db", dict(reminders))

def schedule_reminder (client, reminder):
    nick, t, channel, remindtime, remindmsg = reminder
    reminddelta = remindtime - time.time()

    if reminddelta > 0:
        reminders[client.server].append(reminder)
        client.schedule(reminddelta, client.say, channel, "{0}: Sent {1}: <{2}> {3}".format(
            t, humanize.naturaltime(reminddelta), nick, remindmsg
        ))

        return True

    return False

def irc_public (client, hostmask, channel, message):
    nick, user, host = util.ircmask_split(hostmask)
    
    if message.startswith('!remind'):
        _, target, msg = message.split(' ', 2)
        dmsg = msg.strip()
        #dmsg, remindmsg = msg.split(':', 1)

        t = target.lower()
       
        if t == "me":
            t = nick.lower()

        matches = pdt.nlp(dmsg)
        if matches != None:
                dtime, flags, spos, epos, mtext = matches[0] # first matched date-like object
                remindtime = time.mktime(dtime.timetuple())
                remindmsg = (msg[:spos] + msg[epos:]).strip()

                reminddelta = remindtime - time.time()
                if schedule_reminder(client, (nick, t, channel, remindtime, remindmsg)):
                    save(client)
                    client.say(channel, "Okay, I'll remind {0} then!".format(t))
                else:
                    client.say(channel, "I'm not a time traveler!")
        else:
                client.say(channel, "Sorry, I didn't catch that....")
