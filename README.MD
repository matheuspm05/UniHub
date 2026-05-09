UniHub — Plataforma Digital de Integração Universitária
1. Introdução

O presente documento apresenta a proposta de desenvolvimento do MVP (Produto Mínimo Viável) denominado UniHub, uma plataforma web voltada para integração acadêmica e social de estudantes universitários.

A aplicação tem como objetivo centralizar informações importantes da vida universitária em um único ambiente digital, permitindo que estudantes encontrem eventos, oportunidades de moradia, suporte acadêmico e interação entre alunos de forma prática e organizada.

O sistema busca melhorar a experiência universitária, especialmente para alunos ingressantes e estudantes vindos de outras cidades, promovendo maior conexão entre a comunidade acadêmica.

2. Problema

Atualmente, estudantes universitários enfrentam dificuldades relacionadas à dispersão de informações importantes da vida acadêmica.

Eventos universitários, oportunidades de moradia, dúvidas sobre disciplinas e interações entre alunos normalmente acontecem de forma descentralizada em grupos de WhatsApp, redes sociais ou comunicação informal.

Além disso, alunos calouros e estudantes de outras cidades frequentemente possuem dificuldade de integração social e acadêmica, devido à ausência de uma plataforma centralizada que facilite essa conexão.

O UniHub surge como uma solução para organizar essas informações em um único ambiente digital, promovendo acessibilidade, interação e colaboração entre estudantes.

3. Público-Alvo

O público-alvo da aplicação são estudantes universitários da Universidade Vila Velha (UVV), incluindo:

Alunos ingressantes (calouros)
Estudantes de períodos avançados
Alunos vindos de outras cidades
Representantes de turma
Atléticas e centros acadêmicos
Estudantes em busca de suporte acadêmico e social
4. Proposta de Valor

O UniHub propõe centralizar funcionalidades essenciais da vida universitária em uma única plataforma digital.

O principal diferencial da solução é a integração entre aspectos acadêmicos e sociais, permitindo que os estudantes encontrem eventos, oportunidades de moradia, suporte acadêmico e interação entre alunos em um ambiente organizado e acessível.

A plataforma busca facilitar a integração universitária, melhorar a comunicação entre estudantes e promover maior participação acadêmica e social.

5. Estrutura de Usuários e Permissões

O sistema contará com controle de acesso baseado em perfis de usuário (roles), garantindo diferentes níveis de permissões dentro da plataforma.

5.1 Usuário Comum

O usuário comum representa o aluno padrão da plataforma.

Permissões:

Visualizar eventos
Salvar eventos na agenda pessoal
Criar anúncios de moradia
Participar do fórum acadêmico
Criar tópicos e responder discussões
Gerenciar apenas os próprios conteúdos

Restrições:

Não pode criar eventos oficiais
Não possui acesso administrativo
Não pode alterar conteúdos de outros usuários
5.2 Moderador / Representante

Representa usuários autorizados, como:

Líderes de atlética
Representantes de turma
Centros acadêmicos
Organizadores universitários

Permissões:

Criar eventos oficiais
Editar os próprios eventos
Gerenciar conteúdos relacionados aos eventos criados
Possuir selo de identificação especial

Restrições:

Não pode alterar permissões do sistema
Não possui controle administrativo total
5.3 Administrador

Usuário com acesso completo ao sistema.

Permissões:

Gerenciar usuários
Aprovar moderadores
Remover conteúdos inadequados
Gerenciar eventos, moradias e fórum
Alterar permissões de usuários
Moderar denúncias e relatórios do sistema

6. Funcionalidades do MVP

O MVP do UniHub será composto pelos seguintes módulos principais:

6.1 Sistema de Usuários
Cadastro de usuários
Login e autenticação
Edição de perfil
Controle de permissões
Solicitação para se tornar moderador
Sistema de selos de perfil

Exemplos de selos:

Aluno
Representante
Atlética
Administrador
6.2 Feed Inicial / Home

A plataforma contará com uma página inicial centralizada contendo:

Eventos recentes
Novos tópicos do fórum
Moradias recém-publicadas
Atualizações recentes da plataforma

O objetivo é transformar a aplicação em um ambiente integrado e dinâmico.

6.3 Sistema de Eventos

Módulo voltado para divulgação de eventos universitários.

Funcionalidades:

Listagem de eventos
Visualização de detalhes
Criação de eventos por moderadores
Categorias de eventos
Salvamento de eventos
Página “Minha Agenda”

Categorias possíveis:

Festa
Palestra
Workshop
Atlética
Extensão
Monitoria

Status possíveis:

Ativo
Cancelado
Encerrado
6.4 Sistema de Moradia Compartilhada

Módulo destinado ao compartilhamento de oportunidades de moradia entre estudantes.

Funcionalidades:

Publicação de anúncios
Visualização de vagas disponíveis
Sistema de filtros
Gerenciamento de anúncios do usuário

Filtros:

Bairro
Faixa de preço
Número de vagas
Próximo à UVV
Aceita dividir quarto

Status dos anúncios:

Disponível
Pausado
Preenchido
6.5 Fórum Acadêmico

Espaço destinado à troca de conhecimento entre estudantes.

Funcionalidades:

Criação de tópicos
Respostas em discussões
Organização por disciplinas e cursos
Visualização de tópicos recentes

Categorias possíveis:

Programação Web
Banco de Dados
Engenharia de Software
Cálculo
Física
6.6 Painel “Meus Conteúdos”

Cada usuário possuirá uma área pessoal para gerenciamento de suas atividades na plataforma.

Conteúdos exibidos:

Minhas moradias
Meus tópicos
Minhas respostas
Eventos salvos
Eventos criados (moderadores)
7. Funcionalidades Futuras

Como possíveis evoluções futuras do sistema, destacam-se:

Sistema de curtidas
Comentários em eventos
Chat entre usuários
Sistema de notificações
Upload de imagens
Aplicativo mobile
Recomendações personalizadas
Integração com calendário acadêmico
8. Requisitos Não Funcionais

Os requisitos não funcionais iniciais incluem:

Interface responsiva
Compatibilidade com dispositivos móveis
Sistema de autenticação segura
Controle de permissões por usuário
Persistência de dados
Boa organização visual
Tempo de resposta adequado
Facilidade de navegação
9. Tecnologias Propostas

A arquitetura inicial do sistema será composta por:

Backend
Flask
Python
Frontend
HTML
CSS
JavaScript
Bootstrap
Jinja2
Banco de Dados
SQLite (desenvolvimento inicial)
10. Arquitetura Inicial do Sistema

A aplicação seguirá uma arquitetura web baseada em:

Frontend renderizado no servidor utilizando Flask + Jinja2
Banco de dados relacional
Sistema de autenticação com sessões
Estrutura modular separando usuários, eventos, moradias e fórum
11. Considerações Finais

O UniHub apresenta-se como uma solução viável para melhorar a experiência universitária, promovendo maior integração entre estudantes e facilitando o acesso a informações acadêmicas e sociais.

O escopo do MVP foi definido de forma estratégica para garantir viabilidade de desenvolvimento dentro do período proposto, mantendo foco nas funcionalidades essenciais e permitindo futuras expansões do sistema.

A proposta combina funcionalidades acadêmicas e sociais em um único ambiente digital, buscando tornar a vida universitária mais organizada, conectada e acessível.

Flask + Jinja2 + Bootstrap + PostgreSQL ou SQLite.
