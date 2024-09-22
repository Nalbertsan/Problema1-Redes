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
