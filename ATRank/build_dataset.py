import random
import pickle
import numpy as np

max_length = 90
random.seed(1234)

with open('../Data/Digital_Music.pkl', 'rb') as f:
  reviews_df, meta_df = pickle.load(f)
  cate_list = pickle.load(f)
  user_count, item_count, cate_count, example_count = pickle.load(f)

gap = np.array([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096])

def proc_time_emb(hist_t, cur_t):
  hist_t = [cur_t - i + 1 for i in hist_t]
  hist_t = [np.sum(i >= gap) for i in hist_t]
  return hist_t

train_set = []
test_set = []
for reviewerID, hist in reviews_df.groupby('reviewerID'):
  pos_list = hist['asin'].tolist()
  tim_list = hist['unixReviewTime'].tolist()
  def gen_neg():
    neg = pos_list[0]
    while neg in pos_list:
      neg = random.randint(0, item_count-1)
    return neg
  neg_list = [gen_neg() for i in range(len(pos_list))]

  valid_length = min(len(pos_list), max_length)
  for i in range(1, valid_length):
    hist_i = pos_list[:i]
    hist_t = proc_time_emb(tim_list[:i], tim_list[i])
    if i != valid_length - 1:
      train_set.append((reviewerID, hist_i, hist_t, pos_list[i], 1))
      train_set.append((reviewerID, hist_i, hist_t, neg_list[i], 0))
    else:
      label = (pos_list[i], neg_list[i])
      test_set.append((reviewerID, hist_i, hist_t, label))

random.shuffle(train_set)
random.shuffle(test_set)

assert len(test_set) == user_count

with open('dataset.pkl', 'wb') as f:
  pickle.dump(train_set, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(test_set, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(cate_list, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump((user_count, item_count, cate_count), f, pickle.HIGHEST_PROTOCOL)