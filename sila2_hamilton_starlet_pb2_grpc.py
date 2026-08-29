"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import sila2_hamilton_starlet_pb2 as sila2__hamilton__starlet__pb2


class HamiltonSTARletFeatureStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InitializeDeck = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/InitializeDeck',
            request_serializer=sila2__hamilton__starlet__pb2.InitializeDeckRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.InitializeDeckResponse.FromString,
        )
        self.PrepareDryLabSequence = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/PrepareDryLabSequence',
            request_serializer=sila2__hamilton__starlet__pb2.PrepareDryLabSequenceRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.PrepareDryLabSequenceResponse.FromString,
        )
        self.TriggerHPLCRun = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/TriggerHPLCRun',
            request_serializer=sila2__hamilton__starlet__pb2.TriggerHPLCRunRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.TriggerHPLCRunResponse.FromString,
        )
        self.AcquireCDSData = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/AcquireCDSData',
            request_serializer=sila2__hamilton__starlet__pb2.AcquireCDSDataRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.AcquireCDSDataResponse.FromString,
        )
        self.PredictRetentionTimes = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/PredictRetentionTimes',
            request_serializer=sila2__hamilton__starlet__pb2.PredictRetentionTimesRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.PredictRetentionTimesResponse.FromString,
        )
        self.ExecuteMethod = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/ExecuteMethod',
            request_serializer=sila2__hamilton__starlet__pb2.ExecuteMethodRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.ExecuteMethodResponse.FromString,
        )
        self.GetStatus = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/GetStatus',
            request_serializer=sila2__hamilton__starlet__pb2.GetStatusRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.GetStatusResponse.FromString,
        )
        self.GetMasterClockSync = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/GetMasterClockSync',
            request_serializer=sila2__hamilton__starlet__pb2.GetMasterClockSyncRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.GetMasterClockSyncResponse.FromString,
        )
        self.GetAuditTrail = channel.unary_unary(
            '/org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature/GetAuditTrail',
            request_serializer=sila2__hamilton__starlet__pb2.GetAuditTrailRequest.SerializeToString,
            response_deserializer=sila2__hamilton__starlet__pb2.GetAuditTrailResponse.FromString,
        )


class HamiltonSTARletFeatureServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InitializeDeck(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PrepareDryLabSequence(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TriggerHPLCRun(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AcquireCDSData(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PredictRetentionTimes(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecuteMethod(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStatus(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMasterClockSync(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAuditTrail(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_HamiltonSTARletFeatureServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'InitializeDeck': grpc.unary_unary_rpc_method_handler(
            servicer.InitializeDeck,
            request_deserializer=sila2__hamilton__starlet__pb2.InitializeDeckRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.InitializeDeckResponse.SerializeToString,
        ),
        'PrepareDryLabSequence': grpc.unary_unary_rpc_method_handler(
            servicer.PrepareDryLabSequence,
            request_deserializer=sila2__hamilton__starlet__pb2.PrepareDryLabSequenceRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.PrepareDryLabSequenceResponse.SerializeToString,
        ),
        'TriggerHPLCRun': grpc.unary_unary_rpc_method_handler(
            servicer.TriggerHPLCRun,
            request_deserializer=sila2__hamilton__starlet__pb2.TriggerHPLCRunRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.TriggerHPLCRunResponse.SerializeToString,
        ),
        'AcquireCDSData': grpc.unary_unary_rpc_method_handler(
            servicer.AcquireCDSData,
            request_deserializer=sila2__hamilton__starlet__pb2.AcquireCDSDataRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.AcquireCDSDataResponse.SerializeToString,
        ),
        'PredictRetentionTimes': grpc.unary_unary_rpc_method_handler(
            servicer.PredictRetentionTimes,
            request_deserializer=sila2__hamilton__starlet__pb2.PredictRetentionTimesRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.PredictRetentionTimesResponse.SerializeToString,
        ),
        'ExecuteMethod': grpc.unary_unary_rpc_method_handler(
            servicer.ExecuteMethod,
            request_deserializer=sila2__hamilton__starlet__pb2.ExecuteMethodRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.ExecuteMethodResponse.SerializeToString,
        ),
        'GetStatus': grpc.unary_unary_rpc_method_handler(
            servicer.GetStatus,
            request_deserializer=sila2__hamilton__starlet__pb2.GetStatusRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.GetStatusResponse.SerializeToString,
        ),
        'GetMasterClockSync': grpc.unary_unary_rpc_method_handler(
            servicer.GetMasterClockSync,
            request_deserializer=sila2__hamilton__starlet__pb2.GetMasterClockSyncRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.GetMasterClockSyncResponse.SerializeToString,
        ),
        'GetAuditTrail': grpc.unary_unary_rpc_method_handler(
            servicer.GetAuditTrail,
            request_deserializer=sila2__hamilton__starlet__pb2.GetAuditTrailRequest.FromString,
            response_serializer=sila2__hamilton__starlet__pb2.GetAuditTrailResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'org.silastandard.instruments.hamiltonstarlet.v1.HamiltonSTARletFeature', rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
