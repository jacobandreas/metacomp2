from .builder import OneShotDataset

from absl import flags
from collections import Counter
import json
import numpy as np
from torchdec.vocab import Vocab
import os

FLAGS = flags.FLAGS
flags.DEFINE_string("semparse_split", "question", "which split of the dataset to use")
flags.DEFINE_string("semparse_dataset", "geography", "which dataset to use")
flags.DEFINE_string("semparse_mrl", "sql", "logical form type")
flags.DEFINE_string("val_fold", "8", "")
flags.DEFINE_string("test_fold", "9", "")

#DATA_DIR = "/x/jda/data/text2sql-data/data"
DATA_DIR = "/x/jda/data/text2sql-data/data/non-sql-data"

def clean(s):
    return s.replace('"', ' " ').replace('(', ' ( ').replace(')', ' ) ')

class SemparseDataset(OneShotDataset):
    def __init__(self, **kwargs):
        dataset = FLAGS.semparse_dataset
        with open(os.path.join(DATA_DIR, dataset)) as fh:
            data = json.load(fh)

        dataset = {
            "train": [],
            "dev": [],
            "test": []
        }
        for query in data:
            sql = query[FLAGS.semparse_mrl][0]
            sql = clean(sql)
            for utt in query["sentences"]:
                built_sql = sql
                built_txt = utt["text"]
                for k, v in utt["variables"].items():
                    built_sql = built_sql.replace(k, v)
                    built_txt = built_txt.replace(k, v)

                built_sql = tuple(built_sql.split())
                built_txt = tuple(built_txt.lower().split())

                if FLAGS.semparse_split == "question":
                    split = utt["question-split"]
                elif FLAGS.semparse_split == "query":
                    split = query["query-split"]
                else:
                    assert False, "unknown split %s" % FLAGS.split

                if split in dataset:
                    dataset[split].append((built_txt, built_sql))
                elif split == FLAGS.val_fold:
                    dataset["dev"].append((built_txt, built_sql))
                elif split == FLAGS.test_fold:
                    dataset["test"].append((built_txt, built_sql))
                else:
                    dataset["train"].append((built_txt, built_sql))

        if FLAGS.TEST:
            dataset["train"] += dataset["dev"]

        #np.random.shuffle(dataset["train"])
        #np.random.shuffle(dataset["dev"])
        #np.random.shuffle(dataset["test"])

        super().__init__(
            dataset["train"],
            dataset["dev"],
            dataset["test"],
            **kwargs
        )