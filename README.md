English

# Challenges:#

It took a few days to reach the current result, as the lack of standardization of the data published in the Official Gazette makes the data coding process difficult. The constant changes are a challenge and create the need to adapt the code for various cases and continue doing so over time. I hope this issue will soon be resolved by our friends in IT, servers of the union (and other entities); *

# Operation of the programs - GENERAL. #

Separating the programs (reason): at first, I started with just one program, I was successful, but it stopped working very quickly, sometimes from one day to the next. Whether due to scraping issues or any other problem like data treatment. For this reason, I separated the programs.

Why first capture the links and not direct JSONs? The solution came over time; the program, without generating links, sometimes did not collect all the data. By first focusing on extracting the links, the process is divided, and any eventual failure is easier to relate to the correct access to the page (the problem could be something else), but here we already take an important step to ensure that all data will be accessed and collected. (Can baixar_todos and coletar_todos be merged? Yes, but that is left for colleagues' improvements)

Operation of each program. They are all integrated by executar_todos.py and bat, operating from Monday to Friday at a pre-determined time.

# baixar_todos.py # 

The objective is to access the union's gazette. The program accesses the union's site and performs the advanced search. You can adapt the code to collect any item from the notice, even all of them. I suggest you do a good analysis of the data you are interested in before starting any of the programs, as this will save you a lot of time. Instead of collecting the data right away, the program searches for all the links available in the search.

# coletar_todos.py #
- The program accesses the links collected by baixar_todos.py, accesses, and collects all the data from the page. You can try to be more specific; I preferred to process the data in my own database. 

# trans_ibama / mte / prev.py #
The three programs report the difficulty and lack of standardization of the collected data, and therefore they were separated so that the error of one does not impact the operation of the other, as the search to compile the data is different in the three cases. If you take the DOU as a whole, perhaps we have more than 100 different data formats that should be identical and covered by a simple regular expression search, but that has not been the case, at least until now. I would be happy to receive any improvements in the code and even discuss it with other interested parties. I leave my contact information for anyone who wants to discuss the project. 

# Contact #

# rubemarsaboia@proton.me #

# Português #

# Desafios: Foram gastos alguns dias para chegar ao resultado atual visto que a falta de padronização dos dados publicados no Diário oficial dificulta o processo de codificação dos dados coletados. As mudanças constantes são um desafio e geram uma necessidade de adaptar o código para vários casos e o continuar fazendo ao decorrer do tempo. Espero que logo essa questão seja solucionada pelos nossos amigos da T.I servidores da união (e demais entes); 


    
# Funcionamentos dos programas - GERAL #

*Separar os programas (motivo): a princípio comecei com apenas um programa, obtive exito, mas parava de funcionar muito rapido, as vezes de um dia para outro. Seja por problemas no scraping ou qualquer outro como problemas no tratamento de dados. Por esse motivo separei os programas. 

*Porque primeiro capturar os links e não json diretos? A solução veio com o tempo, o programa sem gerar links por algumas vezes não coletava todos os dados. Ao focar primeiro na extração dos links o processo é dividido e uma eventual falha fica mais fácil de ser relacionada ao acesso correto da página (o problema pode ser outro) mas aqui já damos um passo importante para garantir que todos dados serão realmente acessados e coletados. (da pra unir baixar_todos e coletar_todos? sim, mas ai fica para as melhorias de colegas) #

* funcionamento de cada programa. Todos eles estã integratos pelo executar_todos.py e bat, tendo funcionamento de segunda a sexta em horário pré-determinado.#

* baixar_todos.py - O objeto é acessar o diário da união, o programa acessa o site da união, e faz a busca avançada, você pode adaptar o código para coletar qualquer item do edital, até mesmo todos, sugiro que faça uma boa análise dos dados que tenha interesse antes de iniciar qualquer um dos programas, isso te poupará muito tempo, ao invez de já coletar os dados o programa busca todos os links disponibizados na busca.#

* coletar_todos.py - O programa acessa os links coletadores por baixar_todos.py, acessa e realiza a coleta de todos os dados da página, você pode tentar ser mais específico, eu preferi tratar os dados em meu próprio BD.#

* trans_ibama / mte / prev.py 
* Os três programas relatam a dificuldade e falta de padrão dos dados coeltados e por isso foram separados, para que o erro de um não impacte no funcionamento do outr, visto que a busca para copilar os dados é diferente nos três casos, e se você pegar o DOU como um todo talvez devemos ter mais de 100 formatos diferentes de dados que deveriam ser idênticos, e contemplados por uma simples busca por expressões regulares, mas não foi o caso, ao menos até agora. Ficarei feliz de receber qualquer melhoria no código e até mesmo discutir isso com outro interessado. Deixo meu contato para qualquer um que deseja discutir o projeto.#

contato 

# rubemarsaboia@proton.me #
