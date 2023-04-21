import sys
sys.path.append('../proto/')
import stock_pb2, stock_pb2_grpc

import grpc
import time
from concurrent import futures


class StockService(stock_pb2_grpc.StockServiceServicer):

    def StockMessage(self, request: stock_pb2.StockRequest, context: grpc.ServicerContext):
        print(f"Server recebeu request para enviar uma mensagem para o cliente!\n")

        stock = request.stock
        quantity = request.quantity
        segment_type = stock_pb2.SegmentType.Name(stock.type)
        message = f"Ação:\nNome: {stock.name}\nPreço: {stock.currentPrice}\nQuantidade: {quantity}\nTipo do Segmento: {segment_type}\nDescrição: {stock.description}\n"
        return stock_pb2.StockResponse(message=message)

    def TotalPriceFunction(self, request: stock_pb2.StockRequest, context: grpc.ServicerContext) -> stock_pb2.FunctionResponse:
        print(f"Server recebeu request para calcular uma função para o cliente (Unary)!\n")

        stock = request.stock
        quantity = request.quantity
        total_price = quantity * stock.currentPrice
        return stock_pb2.FunctionResponse(totalPrice=total_price)
    
    def TotalPriceFunctionClientStreaming(self, request_iterator: stock_pb2.StockRequest, context: grpc.ServicerContext):
        print(f"Server recebeu request para calcular uma função para o cliente (Client Streaming)!")

        total_price = 0
        for request in request_iterator:
            print(f"Nome: {request.stock.name} - Quantidade: {request.quantity} - Preço: {request.stock.currentPrice}")

            total_price += request.quantity * request.stock.currentPrice
            time.sleep(1)

        print()
        return stock_pb2.FunctionResponse(totalPrice=total_price)

    def TotalPriceFunctionServerStreaming(self, request: stock_pb2.StockRequest, context: grpc.ServicerContext):
        print(f"Server recebeu request para calcular uma função para o cliente (Server Streaming)!\n")
        
        stock = request.stock
        quantity = request.quantity
        price_history = stock.priceHistory
        response = stock_pb2.FunctionResponse()
        i = 1
        for price in price_history:
            response.totalPrice = price * quantity
            print(f"Server retornando o preço total considerando o {i}º historico de preços da ação!\n")
            time.sleep(1)
            i += 1
            yield response

    def TotalPriceFunctionBiDirectionalStreaming(self, request_iterator: stock_pb2.StockRequest, context: grpc.ServicerContext):
        print(f"Server recebeu request para calcular uma função para o cliente (Bi-Directional Streaming()!\n")

        for request in request_iterator:
            stock = request.stock
            total_price = request.quantity * stock.currentPrice
            response = stock_pb2.FunctionResponse(totalPrice=total_price)
            print(f"Nome: {stock.name} - Quantidade: {request.quantity} - Preço: {stock.currentPrice}")
            time.sleep(1) 
            yield response

        print()

    def TotalPriceFile(self, request: stock_pb2.FileRequest, context: grpc.ServicerContext):
        print(f"Server recebeu request para escrever o preço total das ações em um arquivo!\n")

        stock = request.stockItem.stock
        total_price = request.stockItem.quantity * stock.currentPrice
        filename = request.filename

        str = f"Nome: {stock.name} - Preço: {stock.currentPrice} - Quantidade: {request.stockItem.quantity} - Total: R${total_price}\n"

        with open(filename, 'a', encoding="utf-8") as f:
            f.write(str)
    
        with open(filename, 'rb') as f:
            contents = f.read()

        f.close()
        
        response = stock_pb2.FileResponse(filename=filename, contents=contents)
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stock_pb2_grpc.add_StockServiceServicer_to_server(StockService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
