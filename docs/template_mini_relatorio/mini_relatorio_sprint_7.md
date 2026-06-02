**INSTITUTO FEDERAL DO ESPÍRITO SANTO**  
**CAMPUS COLATINA**  
**BACHARELADO EM SISTEMAS DE INFORMAÇÃO**  
**LABORATÓRIO DE ENGENHARIA DE SOFTWARE**  
**PROF.: JAIMEL DE OLIVEIRA LIMA**

**Aluno(s) / Grupo: Lucas Garcia, Luís Augusto e Pedro Emanuel**  
**Entrega/Sprint: Sprint 7**  
**Data prevista de entrega: 13/04**  
**Data de envio: 13/04**

**1\. SITUAÇÃO DA ENTREGA** (Marque uma das opções)  
(x) Entrega Total  
(   ) Entrega Parcial (mínimo 50%) com notificação  
(   ) Entrega Parcial (mínimo 50%) sem notificação  
(   ) Entrega parcial (menos de 50% da sprint inicial).

**2\. JUSTIFICATIVA** (preencher apenas em caso de atraso, informando os problemas encontrados até sexta-feira)

Não se aplica. A sprint foi concluída integralmente dentro do prazo previsto, sem atrasos.

**3\. O QUE FOI ENTREGUE**

Nesta Sprint 7, foi entregue a API de busca do sistema IFESDOC, contemplando o endpoint responsável por receber consultas textuais, validar os parâmetros informados, integrar a requisição com o mecanismo de busca e retornar uma resposta estruturada com os documentos encontrados. A API também passou a suportar paginação dos resultados, permitindo controlar a quantidade de itens retornados por página.

Também foi implementado e validado o mecanismo de consistência e monitoramento da indexação. Essa entrega incluiu a verificação entre documentos armazenados e registros presentes no índice invertido, permitindo identificar documentos sem versão ativa, documentos sem índice, entradas órfãs e termos inconsistentes. Além disso, foram disponibilizadas métricas básicas de indexação, como quantidade de documentos indexados, quantidade de termos, postagens no índice, taxa de sucesso, erros e logs recentes do processo.

Foi entregue ainda o mecanismo de ranking e limitação de resultados, responsável por ordenar os documentos retornados conforme sua relevância em relação à consulta. O ranking considera critérios como frequência dos termos, peso do termo no índice, posição inicial no documento e cobertura dos termos pesquisados, mantendo também a limitação e paginação dos resultados para preservar o desempenho e a usabilidade.

Por fim, foi realizada uma melhoria no algoritmo de ranking de busca, separando a lógica de cálculo de relevância em uma estratégia própria e adicionando critérios adicionais, como priorização por cobertura de termos, ocorrência de termos no título e recência do documento. Essa melhoria torna a ordenação dos resultados mais consistente e facilita futuras evoluções no mecanismo de busca.

Além das funcionalidades principais, foram realizados ajustes de integração e validação para garantir que o backend, o frontend e os containers principais do sistema continuassem funcionando corretamente após as alterações.

**4\. O QUE NÃO FOI ENTREGUE**

Não houve pendências em relação às funcionalidades planejadas para esta sprint. As issues relacionadas à API de busca, monitoramento da indexação, ranking e melhoria do algoritmo de ranking foram concluídas.

Foi identificado apenas um ponto de melhoria futura relacionado a aspectos de segurança do sistema. Esse ponto não impediu a entrega da sprint, mas deverá ser tratado em uma nova issue específica para revisão e fortalecimento de práticas de segurança.

**5\. DIFICULDADES ENCONTRADAS**

Não foram encontrados impedimentos técnicos durante a sprint. As funcionalidades planejadas puderam ser implementadas, integradas e validadas sem bloqueios relevantes.

Durante a validação final, foi observada a necessidade de criar futuramente uma issue específica para tratar melhorias de segurança, como revisão de logs, exposição de informações sensíveis e endurecimento geral dos fluxos autenticados.

**6\. COMO AS DIFICULDADES FORAM RESOLVIDAS**

Como não houve impedimentos técnicos, não foi necessário adotar medidas corretivas emergenciais durante a sprint.

A necessidade de melhoria futura em segurança foi registrada como ponto de atenção para evolução do sistema. A solução adequada será criar uma nova issue dedicada, permitindo tratar esse tema com escopo próprio, critérios de aceitação claros e validações específicas.

**7\. AUTOAVALIAÇÃO**

| Critério | Avaliação (1 a 5) |
| :---- | :---- |
| Organização do trabalho | 5 |
| Cumprimento do planejamento | 5 |
| Qualidade da entrega | 4 |
| Colaboração do grupo | 5 |
