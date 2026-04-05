**INSTITUTO FEDERAL DO ESPÍRITO SANTO**  
**CAMPUS COLATINA**  
**BACHARELADO EM SISTEMAS DE INFORMAÇÃO**  
**LABORATÓRIO DE ENGENHARIA DE SOFTWARE**  
**PROF.: JAIMEL DE OLIVEIRA LIMA**

**Aluno(s) / Grupo: Lucas Garcia, Luís Augusto e Pedro Emanuel**  
**Entrega/Sprint: Sprint 4**  
**Data prevista de entrega: 31/03**  
**Data de envio: 31/03**

**1\. SITUAÇÃO DA ENTREGA** (Marque uma das opções)  
(x) Entrega Total  
(   ) Entrega Parcial (mínimo 50%) com notificação  
(   ) Entrega Parcial (mínimo 50%) sem notificação  
(   ) Entrega parcial (menos de 50% da sprint inicial).

**2\. JUSTIFICATIVA** (preencher apenas em caso de atraso, informando os problemas encontrados até sexta-feira)

Não se aplica. A sprint foi concluída integralmente dentro do prazo previsto, sem atrasos.

**3\. O QUE FOI ENTREGUE**

Nesta Sprint 4, foi entregue a estrutura de armazenamento de documentos do sistema IFESDOC, contemplando a definição do local de armazenamento, organização dos arquivos, registro de metadados no banco de dados e mecanismos de recuperação dos documentos armazenados.

Também foi implementado o fluxo de upload e validação de documentos, com endpoint dedicado para envio de arquivos, validações de tipo, tamanho e consistência dos documentos, integração com a estrutura de armazenamento e registro das informações necessárias para o processamento posterior.

Além disso, foi entregue a funcionalidade de extração de conteúdo de documentos, permitindo identificar o tipo de arquivo enviado e extrair conteúdo textual de formatos suportados, como PDF, DOCX e TXT, armazenando esse conteúdo para uso no pipeline interno de ingestão, processamento e indexação.

Por fim, foi consolidado o controle de acesso e os logs administrativos do sistema, garantindo proteção de endpoints administrativos com base no perfil do usuário, bloqueio de acessos não autorizados e registro de ações relevantes para auditoria, como operações administrativas e eventos ligados à ingestão de documentos.

**4\. O QUE NÃO FOI ENTREGUE**

Não houve pendências em relação às funcionalidades planejadas para a Sprint 4. As issues previstas para armazenamento de documentos, upload e validação, extração de conteúdo e controle de acesso com logs administrativos foram concluídas.

**5\. DIFICULDADES ENCONTRADAS**

Durante a sprint, houve dificuldade com um bug de autenticação no frontend, especificamente na tela de gerenciamento de usuários, impactando o funcionamento esperado do CRUD de usuários em determinados fluxos autenticados.

Também surgiram problemas relacionados ao armazenamento e ao reconhecimento dos documentos enviados para ingestão, principalmente na identificação correta dos arquivos processados e no encadeamento entre upload, registro e recuperação posterior.

Outra dificuldade ocorreu no processo interno de ingestão, em especial na integração entre as etapas do pipeline responsáveis por receber, validar, interpretar e encaminhar os documentos para extração e processamento.

**6\. COMO AS DIFICULDADES FORAM RESOLVIDAS**

O problema de autenticação no frontend foi resolvido com ajustes no fluxo de autenticação e na integração entre tela de gerenciamento de usuários e backend, garantindo o funcionamento correto das operações do CRUD sob contexto autenticado.

As falhas ligadas ao armazenamento e reconhecimento dos documentos foram solucionadas com correções na lógica de persistência e identificação dos arquivos ingeridos, permitindo que os documentos fossem registrados e recuperados corretamente dentro da estrutura definida pelo sistema.

Já as dificuldades do processo interno de ingestão foram resolvidas com ajustes na integração entre as etapas do pipeline, refinando o fluxo entre upload, validação, armazenamento, extração de conteúdo e tratamento dos documentos, até estabilizar o comportamento esperado.

**7\. AUTOAVALIAÇÃO**

| Critério | Avaliação (1 a 5) |
| :---- | :---- |
| Organização do trabalho | 4 |
| Cumprimento do planejamento | 5 |
| Qualidade da entrega | 4 |
| Colaboração do grupo | 5 |

