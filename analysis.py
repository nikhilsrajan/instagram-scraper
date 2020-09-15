import config
import matplotlib.pyplot as plt
import datetime as dt

datetimes = []
post_count = 0
post_ids = []
with open(config.datetimes_file, 'r') as fin:
    for line in fin:
        line = line.replace('.000Z\n', '')
        datetime = dt.datetime.fromisoformat(line)
        datetimes.append(datetime)
        post_ids.append(post_count)
        post_count -= 1

plt.plot_date(datetimes, post_ids)
plt.tight_layout()
plt.show()