from errbot import BotPlugin, botcmd
from optparse import OptionParser
import requests


class HostedGraphite(BotPlugin):

    def get_configuration_template(self):
        """ configuration entries """
        config = {
            'status_url': '',
        }
        return config

    def _check_config(self, option):

        # if no config, return nothing
        if self.config is None:
            return None
        else:
            # now, let's validate the key
            if option in self.config:
                return self.config[option]
            else:
                return None

    def _get_status(self, results):
        '''
        Returns statuspage api results
        :param results: number of results to return
        :return: list
        '''

        status_url = self._check_config('status_url') or 'http://6j73b8w0lj03.statuspage.io/api/v2/summary.json'
        request = requests.get(status_url)

        if not request.ok:
            self.log.info('Unable to reach {}'.format(self.config['status_url']))
            return []

        summary = request.json()
        self.log.debug(summary)

        incidents = summary['incidents'][0:results]
        return incidents

    @botcmd(split_args_with=' ')
    def hostedgraphite_status(self, msg, args):
        '''
        This returns the latest status from their status page
        options:
            results: number of results to return (default: 5)
        '''

        parser = OptionParser()
        parser.add_option("--results", dest="results", type='int', default=5)
        (options, t_args) = parser.parse_args(args)
        data = vars(options)

        incidents = self._get_status(data['results'])

        results = []
        count = 1
        for incident in incidents:
            results.append('{count}. ({updated}) {name} - {last_update} Status: {status}, Created: {created}. {update_count} Updates. {link}'.format(
                count=count,
                updated=incident['updated_at'],
                name=incident['name'],
                last_update=incident['incident_updates'][0]['body'],
                status=incident['status'],
                created=incident['created_at'],
                update_count=len(incident['incident_updates']),
                link=incident['shortlink']
            ))
            count += 1

        if results:
            response = ' '.join(results)
        else:
            response = 'No incidents reported.'

        self.send(msg.frm,
                  response,
                  message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)
