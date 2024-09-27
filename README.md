Para rodar esta aplicação, é necessário ter Docker e Python 3.10 ou superior instalados na máquina.

### Como rodar o Servidor

Primeiramente, será necessário baixar a imagem Docker do servidor. Para isso, execute o comando:

docker pull nalbertsan/serverpbl:1.1

Após o download da imagem, você deve rodar uma instância do container. Use o comando abaixo para isso:

docker run -d --name serverpbl -p <porta_local>:<porta_container> nalbertsan/serverpbl:1.1

Substitua `5000` e `5000` pelas portas desejadas, garantindo que a porta local esteja disponível.

### Como rodar o Cliente

1. Faça o download ou clone o repositório do cliente. A pasta necessária para rodar o cliente é chamada "Client". Se estiver utilizando `git`, use o comando:

git clone [<URL_DO_REPOSITORIO>](https://github.com/Nalbertsan/Problema1-Redes/)

2. Acesse a pasta "Client", onde os arquivos do cliente estão localizados. Isso pode ser feito com o seguinte comando:

cd Client

3. Agora, basta rodar o arquivo `main.py`. Para isso, certifique-se de que o Python 3.10 ou superior está instalado e configurado corretamente, e execute o comando:

python main.py

Com isso, o cliente será iniciado e se comunicará com o servidor rodando em Docker.

### Observações

- Certifique-se de que o servidor está rodando corretamente antes de iniciar o cliente.
- Verifique as configurações de portas e quaisquer bloqueios de firewall que possam interferir na comunicação entre cliente e servidor.


# Introdução

Com o crescimento das companhias aéreas de baixo custo, surgiu a necessidade de sistemas automatizados para compra de passagens pela Internet. Uma nova companhia brasileira busca implementar uma solução que permita aos clientes reservarem trechos de voos via TCP/IP, garantindo eficiência e disponibilidade. Este relatório descreve o desenvolvimento de um sistema utilizando a linguagem Python e a API Socket para comunicação direta entre clientes e servidor, sem o uso de frameworks externos. A solução foi testada em contêineres Docker, garantindo escalabilidade e gestão eficiente das instâncias, permitindo reservas de trechos de forma robusta e em tempo real.

# Como a arquitetura foi desenvolvida. Quais os componentes e seus papeis nessa arquitetura.

## 1. Cliente (Client)
Função: Os clientes se conectam ao servidor via TCP para consultar a disponibilidade de trechos de voos e fazer reservas. Cada cliente pode escolher e reservar trechos, e quem realizar a reserva primeiro garante a preferência.
Papel na Arquitetura:
Envia requisições de consulta e reserva de trechos.
Recebe respostas do servidor com a confirmação ou erro.
## 2. Servidor (Server)
Função: O servidor central gerencia todas as interações com os clientes, processando solicitações de consulta e reserva de trechos.
Papel na Arquitetura:
Recebe requisições dos clientes.
Verifica a disponibilidade de trechos no banco de dados.
Atualiza a base de dados com as reservas feitas e responde aos clientes.
## 3. Outros Componentes
Protocolo de Comunicação (TCP/IP): Define a troca de dados estruturada e confiável entre o cliente e o servidor, garantindo a entrega e a integridade das mensagens.
Contêineres Docker: Facilita a execução e escalabilidade do sistema, permitindo rodar várias instâncias de clientes e servidores de forma isolada e eficiente.
Gerenciamento de Trechos: A lógica interna no servidor que garante a consistência das reservas, evitando duplicidade de trechos e assegurando que o primeiro cliente a reservar tenha a preferência.

# Que paradigma de serviço foi usado (stateless ou statefull)? Qual(is) o(s) motivo(s) dessa escolha.

## Motivo da Escolha:
O sistema foi desenvolvido utilizando um paradigma stateful porque ele precisa manter o estado das reservas de trechos durante a interação com os clientes. Ou seja, o servidor deve rastrear quais trechos foram reservados e garantir que um cliente, após iniciar o processo de compra, tenha preferência sobre os trechos selecionados até a finalização da transação.
Esse paradigma foi escolhido por dois motivos principais:
Consistência nas Reservas: O servidor precisa garantir que uma vez que um cliente reserve um trecho, este não seja oferecido a outros clientes, exigindo que o estado da transação seja mantido ao longo da sessão.
Processo de Compra em Múltiplos Passos: Como o cliente pode selecionar vários trechos (voos) em sequência, o servidor deve manter o histórico dessa escolha para completar a compra, o que requer um modelo stateful.

# Que protocolo de comunicação foi desenvolvido entre os componentes do sistema? Quais as mensagens e a ordem das mensagens trocadas.

## Protocolo de Comunicação usado foi TCP/IP
Mensagens Trocadas e Ordem:
### Requisição de Disponibilidade:
Cliente → Servidor: O cliente envia uma mensagem solicitando a lista de trechos disponíveis.
Servidor → Cliente: O servidor responde com a lista de trechos disponíveis, incluindo detalhes como origem e destino
### Solicitação de Reserva:
Cliente → Servidor: Após escolher um trecho, o cliente envia uma mensagem de reserva especificando o voo desejado.
Servidor → Cliente: O servidor verifica a disponibilidade do trecho e, se disponível, confirma a reserva ao cliente. Caso o trecho já esteja reservado, o servidor envia uma mensagem de erro.
### Confirmação de Compra:
Cliente → Servidor: O cliente confirma a compra dos trechos reservados.
Servidor → Cliente: O servidor finaliza a transação e envia uma confirmação da compra ou um erro caso algo falhe.
### Ordem das Mensagens:
Consulta → 2. Reserva → 3. Confirmação da Compra.
Esse fluxo garante que os trechos sejam consultados, reservados e comprados de forma organizada e com controle sobre a disponibilidade.

# Que tipo de formatação de dados foi usada para transmitir os dados, permitindo que nós de diferentes sistemas e implementadas em diferentes linguagens compreendam as mensagens trocadas.

## Formatação de Dados: JSON (JavaScript Object Notation)
O JSON foi escolhido como formato de transmissão de dados porque:

Simplicidade e Leveza: É fácil de ler e escrever, tanto para humanos quanto para máquinas.

Interoperabilidade: É amplamente suportado por diversas linguagens de programação, permitindo que diferentes sistemas, mesmo implementados em linguagens distintas, compreendam e processem as mensagens trocadas.

Estrutura Flexível: Permite representar os dados de forma estruturada, como listas de trechos de voos, status de reservas e confirmações.

O uso de JSON facilita a troca de informações, mantendo o sistema eficiente e compatível com diversas plataformas.

# O sistema permite a realização de compras de passagens de forma paralela ou simultânea? Como é possivel otimizar o paralelismo do sistema.

O sistema permite que vários clientes realizem compras simultaneamente. Isso é possível porque o servidor controla o acesso aos trechos de voos, garantindo que, ao reservar um trecho, ele seja bloqueado para outros clientes até a transação ser concluída ou expirar. Esse controle evita conflitos em reservas feitas em paralelo. E a otimização do paralelismo foi realizada fazendo com que a solicitação de cliente pode ser processada em uma thread ou processo separado, permitindo que múltiplos pedidos sejam atendidos ao mesmo tempo.

# Há problemas de concorrência decorrentes do uso de conexões simultâneas? Se sim, como estas questões foram tratadas?

Para evitar conflitos em conexões simultâneas, o servidor implementa um mecanismo de bloqueio (lock) para cada trecho de voo. Quando um cliente tenta reservar um trecho, esse trecho é temporariamente bloqueado até a confirmação ou cancelamento da compra, evitando que outros clientes reservem o mesmo trecho simultaneamente.

## Sincronização de Acesso: 
Durante o processamento de múltiplas requisições, o servidor garante que as atualizações no banco de dados de trechos sejam feitas de forma atômica, assegurando que apenas um cliente por vez consiga reservar ou modificar o estado de um trecho.

Essas estratégias garantem que o sistema lide de maneira eficiente com conexões simultâneas, evitando inconsistências nas reservas.

# O sistema utiliza algum mecanimos para melhorar o tempo de resposta (uso de cache, filas, threads, etc.)? Como você avaliou o desempenho do seu sistema? Fez algum teste de desempenho?

Para melhorar o tempo de resposta do sistema, foram implementados mecanismos de concorrência utilizando threads. Isso permite que múltiplos clientes possam realizar compras de passagens simultaneamente, sem que um processo interfira no outro. Esse paralelismo ajuda a otimizar o uso do servidor e garantir que as requisições sejam processadas de maneira eficiente, diminuindo a latência.

O desempenho do sistema foi avaliado através de testes de estresse em ambiente Docker, simulando múltiplos clientes conectados ao servidor. Foram observados o tempo de resposta das requisições e o comportamento do servidor sob carga. Não foram utilizados mecanismos de cache ou filas.

# Tirando e recolocando o cabo de algum dos nós, o sistema continua funcionando? Ele continua podendo fazer a compra que iniciou anteriormente?

O sistema não foi projetado para lidar com falhas de rede, como a desconexão de um nó. Se o cabo for retirado durante uma compra, a conexão com o servidor será perdida e a compra será interrompida. Quando o nó é reconectado, o cliente precisará reiniciar o processo de compra. Não há suporte para retomada automática de transações incompletas após a falha de rede.

# Conclusão

Por fim, podemos dizer que o sistema de compra de passagens aéreas foi criado usando comunicação TCP/IP e contêineres Docker. Isso permite que vários clientes consultem e reservem trechos de voos simultaneamente. Ao usar um protocolo personalizado e uma arquitetura stateful para controlar as reservas, o sistema atingiu seu objetivo de fornecer uma solução de troca de mensagens sem frameworks.

Ao avançar, muito foi aprendido, principalmente sobre tópicos como o controle de concorrência e a comunicação direta entre clientes e servidores por meio de sockets TCP. Além disso, o uso de Docker ajudou a entender melhor como os contêineres podem ajudar na escalabilidade, implantação e teste de sistemas distribuídos. O trabalho com um sistema stateful demonstrou que garantir a consistência dos dados em ambientes com vários usuários operando simultaneamente é crucial. O conhecimento pode ser usado em várias situações, como otimizar serviços baseados em contêineres e criar sistemas que precisam de comunicação eficiente em tempo real. Além disso, é possível ampliar a experiência com controle de concorrência e sincronização para outras soluções de software onde o desempenho e a consistência dos dados são importantes.
