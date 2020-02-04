from __future__ import print_function

import grpc
import tensorflow as tf

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

# tf.app.flags.DEFINE_string('server', 'localhost:9000',
#                            'PredictionService host:port')
# tf.app.flags.DEFINE_string('image', '', 'path to image in JPEG format')
# FLAGS = tf.app.flags.FLAGS

def predict(server, image):

    channel = grpc.insecure_channel(server)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    # Send request
    with open(image, 'rb') as f:
        # See prediction_service.proto for gRPC request/response details.
        data = f.read()
        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'inception'
        request.model_spec.signature_name = 'predict_images'
        request.inputs['images'].CopyFrom(
            tf.contrib.util.make_tensor_proto(data, shape=[1]))
        result_ = stub.Predict(request, 10.0)  # 10 secs timeout

    result = []
    for i in range(3):
        result.append({'label': result_.outputs['classes'].string_val[i].decode('utf-8'), 'score' : round(result_.outputs['scores'].float_val[i], 4)})

    return result