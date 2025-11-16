from segmentJson import filterData

# Return a list of days and their mean tput_mbps
#  Each item in the list will be in the form:
#  YEAR_MONTH_DAY MEAN_TPUT mbps
#  Example: 2024-06-02 12.123 mbps
def dailyMeans(dataset):
  days: set = {entry['timestamp'][0:10] for entry in dataset}
  daily_means = []
  for day in days:
    tputs = [ float(entry['median_tput_mbps']) for entry in dataset if entry['timestamp'].startswith(day) ]
    mean_tput = sum(tputs) / len(tputs)
    daily_means.append( day + ' ' + str(mean_tput) + ' mbps')

  return sorted(daily_means)

# Return a list of days and their maximum tput_mbps
#  Each item in the list will be in the form:
#  YEAR_MONTH_DAY MAX_TPUT mbps
#  Example: 2024-06-02 100.456 mbps
def dailyPeaks(dataset):
  days: set = {entry['timestamp'][0:10] for entry in dataset}
  daily_peaks = []
  for day in days:
    tputs = [ float(entry['max_tput_mbps']) for entry in dataset if entry['timestamp'].startswith(day) ]
    max_tput = max(tputs)
    daily_peaks.append( day + ' ' + str(max_tput) + ' mbps')

  return sorted(daily_peaks)
