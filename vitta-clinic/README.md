# Vitta Clinic

Sistema demonstrativo de gestão de clínica feito somente com HTML5, CSS3 e JavaScript vanilla. Não requer instalação, servidor, frameworks ou bibliotecas externas.

## Como executar

1. Extraia a pasta `vitta-clinic` mantendo a estrutura de arquivos.
2. Abra `index.html` diretamente em um navegador atualizado.
3. Entre com uma das contas de demonstração abaixo. Os registros ficam salvos no `localStorage` do navegador usado.

### Credenciais de demonstração

| Perfil | E-mail | Senha |
| --- | --- | --- |
| Administrador | `admin@vitta.com` | `123456` |
| Médico | `medico@vitta.com` | `123456` |
| Recepcionista | `recepcao@vitta.com` | `123456` |

Use o botão **Sair** para encerrar a sessão. Para reiniciar os registros demonstrativos, remova os itens `vitta-clinic-db-v1` e `vitta-clinic-session-v1` do armazenamento local do site no navegador e recarregue a página.

## Funcionalidades

- Sessão persistente, login e navegação conforme o perfil.
- Dashboard com indicadores, próximas consultas e gráfico mensal.
- Cadastro, edição, busca, paginação e exclusão confirmada de pacientes, médicos, especialidades e consultas.
- Formatação do CPF sem validar dígitos verificadores, unicidade de CPF/CRM e validação de data de agendamento.
- Prontuários vinculados a paciente e consulta, com histórico cronológico; gravação disponível para médicos e administradores.
- Relatórios de consultas por período, consultas por médico e pacientes cadastrados, com impressão.
- Layout responsivo, etiquetas acessíveis, estados vazios e notificações.

## Estrutura

```text
vitta-clinic/
├── index.html
├── Back/        # API Flask separada (instruções em Back/README.md)
├── pages/       # Dashboard e módulos da aplicação
├── css/         # Reset, tokens, estilos compartilhados e responsividade
├── js/          # Autenticação, persistência, seed, utilitários e módulos
├── assets/      # Logo e recursos visuais
└── data/        # Exemplo de estrutura do banco (db.json)
```

O backend REST opcional fica em [Back/README.md](./Back/README.md). O front-end permanece em modo demonstrativo com `localStorage`; conectá-lo à API exige trocar a camada de persistência do navegador por chamadas HTTP autenticadas.

## Observação de segurança

Esta aplicação é exclusivamente uma demonstração front-end. A autenticação, os perfis e os dados são simulados no navegador e podem ser inspecionados ou alterados pelo usuário. Não utilize credenciais reais, dados pessoais de pacientes nem informações clínicas reais. Um sistema de produção requer backend, controles de acesso no servidor, criptografia, auditoria e conformidade com a legislação aplicável.
