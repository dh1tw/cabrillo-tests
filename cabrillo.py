import os
import argparse
from datetime import datetime
from pyhamtools import LookupLib, Callinfo

# basic implementation of a QSO object
class QSO(object):

    def __init__(self):
        self.freq = None
        self.date = None
        self.mode = None
        self.own_call = None
        self.own_call_info = None # later filled with pyhamtools
        self.rst_sent = None
        self.xchg_sent = None
        self.partner_call = None
        self.partner_call_info = None # later filled with pyhamtools
        self.rst_rcvd = None
        self.xchg_rcvd = None

    def export_string(self):
        return ("{0};{1};{2};{3};{4};{5};{6};{7},{8},{9}\n".format(self.freq,
            self.mode,
            self.date.strftime("%m/%d/%Y;%H:%M"),
            self.own_call,
            self.own_call_info.get("country"),
            self.rst_sent,
            self.xchg_sent,
            self.partner_call,
            self.partner_call_info.get("country"),
            self.rst_rcvd,
            self.xchg_rcvd))

# basic implementation of a cabrillo importer class
class Importer(object):

    def __init__(self):
        pass

    def parse(self, log_file):
        lines = []
        try:
            file = open(log_file, "r")
            for line in file:
                lines.append(line)
            file.close()
        except IOError:
            print "unable to find file " + log_file

        # depending on the contest, the content of the cabrillo file (e.g.
        # exchange rapports might be different)
        header = self._extract_header(lines)

        qsos = []

        # not sure if the header length is always the same. Maybe a better
        # function should be implemented to reliably stip of the header.

        # We also want to remove the last line of the file.
        log_without_header_and_footer = lines[17:len(lines)-1]

        for line in log_without_header_and_footer:
            try:
                # let's assume the contest has been identified as CQWW
                qso = self._parse_qso_cqww(line)
                qsos.append(qso)
            except ValueError as e:
                print e, line
            # except:
            #     print "unable to process qso line: " + line

        return qsos

    def _extract_header(self, lines):
        # I leave the implementation of this method up to you
        pass

    def _parse_qso_cqww(self, qso_line):

        # we don't care about the header for now
        if qso_line.startswith("QSO: ") == False:
            raise ValueError("invalid QSO line")

        freq = int(qso_line[5:11])
        mode = qso_line[11:14].strip()
        date = datetime.strptime(qso_line[14:30].strip(), '%Y-%m-%d %H%M')
        own_call = qso_line[30:44].strip()
        rst_sent = int(qso_line[44:48])
        xchg_sent = int(qso_line[48:55])
        partner_call = qso_line[55:69].strip()
        rst_rcvd = int(qso_line[69:73])
        xchg_rcvd = int(qso_line[73:])

        qso = QSO()
        qso.freq = freq
        qso.mode = mode
        qso.date = date
        qso.own_call = own_call
        qso.rst_sent = rst_sent
        qso.xchg_sent = xchg_sent
        qso.partner_call = partner_call
        qso.rst_rcvd = rst_rcvd
        qso.xchg_rcvd = xchg_rcvd

        return qso

if __name__ == "__main__":

    # instanciate a Importer object
    cabImporter = Importer()

    # parse the provided file
    qsos = cabImporter.parse("./k1ir.log")

    # I suggest to use ClublogXML instead. Clublog is the best lookupDB.
    # But you need an API key which you can request on the clublog website.
    print "loading country files... this might take 10-30s"
    my_lookuplib = LookupLib(lookuptype="countryfile")
    cic = Callinfo(my_lookuplib)

    for qso in qsos:
        try:
            qso.own_call_info = cic.get_all(qso.own_call)
            qso.partner_call_info = cic.get_all(qso.partner_call)
        except KeyError:
            print "unable to get infos for " + qso.own_call

    f = open("enriched_log.txt", "w")
    for qso in qsos:
        f.write(qso.export_string())
    f.close()





