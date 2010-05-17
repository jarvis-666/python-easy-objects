class DictObj ( dict ):
  "A wrapper for dictionaries that feel like py objects"
  def __getattr__(self, key):
    if key in self:
      return self[key]
    else:
      try:
        return super(DictObj, self).__getattr__(key)
      except:
        pass
    return None

import csv

def fix_name(n):
  'Fixes a string to be nicer (useable) variable names.'
  return n.replace(' ','_').replace('.','_')

def read_csv(inf, close_file=True):
  'Reads a csv file in as a list of objects'
  def from_csv_line(l, h):
    return DictObj(dict(zip(h, l)))
  iter = csv.reader(inf).__iter__()
  header = map(fix_name, iter.next())
  for i in iter:
    yield from_csv_line(i, header) 
  if close_file:
    inf.close()

def write_csv(out, objs, cols=None, close_file=True):
  'Writes a list of dicts out as a csv file.'
  def to_csv_line(obj, header):
    def lookup_or_empty(o, k, default=''):
      if k in o:
        return o[k]
      return default
    return map(lambda h : lookup_or_empty(obj,h), header)
  iter = objs.__iter__()
  output = csv.writer(out)
  first = iter.next()
  if cols is None:
    cols = sorted(first.keys())
  output.writerow(cols)
  output.writerow(to_csv_line(first, cols))
  output.writerows(map(lambda x: to_csv_line(x, cols), iter))
  if close_file:
    out.close()

def db_query(host, db, query, user, pw):
  "A mysql database query to python objects"
  cmd = 'mysql -h%s -u%s -p%s -e"%s" %s' 
  f = os.popen(cmd % (host, user, pw, query, db))
  header = map(fix_name, f.readline().strip().split('\t'))
  for line in f:
    yield DictObj(dict(zip(header, line.strip().split('\t'))))
  f.close()

#holdings = db_query("portfolio_machine", "portfolios", "john", "********", "select symbol, quantity from holdings where userid = 12345;")
holdings = map(lambda x:DictObj({'symbol':x[0],'quantity':x[1]}), 
  [('GOOG','10'), ('AAPL', '11'), ('IBM', '20'), ('NFLX', '5'), ('F', '8')])

import urllib2
def get_quotes(symbol, start_y, start_m, start_d, end_y, end_m, end_d):
  url = 'http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s&g=d&ignore=.csv' \
      % (symbol, start_m-1, start_d, start_y, end_m-1, end_d, end_y)
  return urllib2.urlopen(url)

def values(q):
  qs = reversed(list(read_csv(get_quotes(q.symbol, 2010,4,1, 2010,4,30))))
  return map(lambda x:(x.Date, float(x.Close) * int(q.quantity)), qs)

def get_perf(hs):
  _1 = lambda x: x[1]
  _0 = lambda x: x[0]
  # Get the performance for each holding
  perf = map(values, holdings)
  # Sum the values together
  total_perf = map(lambda x: (_0(_0(x)), sum(map(_1, x))), zip(*perf))
  return total_perf

print "-- Holdings --"
for h in holdings:
  print '%s: %s' % (h.symbol,h.quantity)
print "-- Performance --"
for x in get_perf(holdings):
  print '%s: %s' % (x[0], x[1])

