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
