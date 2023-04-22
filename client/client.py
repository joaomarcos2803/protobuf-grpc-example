import sys
sys.path.append('../proto/')
import stock_pb2, stock_pb2_grpc
import grpc
import time

def menu():
    print('Please choose an option:')
    print('1. Receber Mensagem da Ação')
    print('2. Calcular Preço Total (Unary RPC)')
    print('3. Calcular Preço Total (Client Streaming RPC)')
    print('4. Calcular Preço Total (Server Streaming RPC)')
    print('5. Calcular Preço Total (Bidirectional Streaming RPC)')
    print('6. Escrever Preço Total em um Arquivo')
    print('7. Sair')

    choice = input('Digite a opção: ')
    return choice


def generate_messages():
    messages = [
        stock_pb2.StockRequest(stock=stock_pb2.Stock(name='AAPL', current_price=142.7, description='Apple Inc.'), quantity=10),
        stock_pb2.StockRequest(stock=stock_pb2.Stock(name='AMZN', current_price=3346.83, description='Amazon.com Inc.'), quantity=5),
        stock_pb2.StockRequest(stock=stock_pb2.Stock(name='GOOGL', current_price=2292.63, description='Alphabet Inc. Class A'), quantity=3),
        stock_pb2.StockRequest(stock=stock_pb2.Stock(name='MSFT', current_price=267.5, description='Microsoft Corporation'), quantity=7)
    ]

    for msg in messages:
        print(f"Cliente enviando a ação {msg.stock.name} para o server!")
        time.sleep(1)
        yield msg

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = stock_pb2_grpc.StockServiceStub(channel)

    while True:
        choice = menu()

        if choice == '1':
            stock = stock_pb2.Stock(name='Google', current_price=1500.0, description='Technology', type= stock_pb2.SegmentType.Value("OTHER"))
            request = stock_pb2.StockRequest(stock=stock, quantity=10)
            response = stub.StockMessage(request)
            print("\nResponse do server:\n")
            print(response.message, '\n')

        elif choice == '2':
            stock = stock_pb2.Stock(name='Amazon', current_price=3000.0, description='E-commerce')
            request = stock_pb2.StockRequest(stock=stock, quantity=5)
            response = stub.TotalPriceFunction(request)
            print('\nResponse do server:\n')
            print('Preço Total:', response.total_price, '\n')

        elif choice == '3':
            response = stub.TotalPriceFunctionClientStreaming(generate_messages())

            print('\nResponse do server:\n')
            print('Preço Total:', response.total_price, '\n')

        elif choice == '4':   
            stock = stock_pb2.Stock(name="AAPL", current_price=146.70, price_history=[145.50, 147.20, 145.00])
            request = stock_pb2.StockRequest(stock=stock, quantity=10)

            print(f"\nResponses de Streaming:")
            for response in stub.TotalPriceFunctionServerStreaming(request):
                print(f"Preço Total: {response.total_price:.2f}")
            print()

        elif choice == '5':
            responses = stub.TotalPriceFunctionBiDirectionalStreaming(generate_messages())

            for response in responses:
                print(f'\nPreço Total:', response.total_price)

            print()

        elif choice == '6':
            stock = stock_pb2.StockRequest(stock=stock_pb2.Stock(name='Google', current_price=8000.0, description='Automotive'), 
            quantity=3)
            
            filename = 'results.txt'
    
            request = stock_pb2.FileRequest(stock_item=stock, filename=filename)
            response = stub.TotalPriceFile(request)

            try: 
                with open(filename, 'wb') as f:
                    f.write(response.contents)

                print("\nArquivo modificado no servidor com sucesso!\n")
            except:
                print("\nErro ao criar o arquivo!\n")

        elif choice == '7':
            break

        else:
            print('Opção inválida!')

if __name__ == '__main__':
    run()