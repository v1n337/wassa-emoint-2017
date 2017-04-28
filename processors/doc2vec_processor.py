import logging

from gensim.models import Doc2Vec
from sklearn import model_selection
from sklearn.svm import LinearSVR

from data.labeledline import LabeledLineSentence
from processors.abstract_processor import Processor
from utils import file_helper

log = logging.getLogger(__name__)


class Doc2VecProcessor(Processor):

    def process(self):
        log.info("Doc2VecProcessor begun")

        input_tweets = file_helper.read_input_data(self.options.training_data_file_path)
        input_tweets_labeled = LabeledLineSentence(self.options.training_data_file_path)
        model = Doc2Vec(input_tweets_labeled, iter=20, workers=8)

        x_train = list()
        y_train = list()
        for tweet in input_tweets:
            x_train.append(model.infer_vector(tweet.text.split()))
            y_train.append(tweet.intensity)

        scores = \
            model_selection.cross_val_score(
                LinearSVR(), x_train, y_train, cv=10, scoring='r2'
            )
        mean_score = scores.mean()

        log.info("Accuracy: %0.2f (+/- %0.2f)" % (mean_score, scores.std() * 2))

        if self.options.test_data_file_path:

            log.info("Making predictions for the test dataset")

            test_tweets = list(file_helper.read_test_data(self.options.test_data_file_path))

            ml_model = LinearSVR()
            ml_model.fit(x_train, y_train)

            x_test = list()
            for tweet in test_tweets:
                x_test.append(model.infer_vector(tweet.text.split()))

            y_test = ml_model.predict(X=x_test)

            with open(self.options.test_data_file_path + ".predicted", 'w') as predictions_file:
                for i in range(len(test_tweets)):
                    predictions_file.write(
                        str(test_tweets[i].id) + "\t" + test_tweets[i].text + "\t" +
                        test_tweets[i].emotion +"\t" + str(y_test[i]) + "\n"
                    )

        log.info("Doc2VecProcessor ended")
