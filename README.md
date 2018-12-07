# RDDS-online-compiler
The compiler is build from scratch with module :-</br>
• Lexical analyser</br>
• Parser</br>
• Intermediate Code Generator</br>
• Error handling</br>
• Symbol table</br>
## LEXICAL ANALYSER AND SCANNER
• First program is run on the source file and then the code is broken into the list of distinct lines.</br>
• at the start of each non-whitespace character, the frst character is used to determine the type of the
token to expect.</br>
• The token is returned if the type is matched without any issue Otherwise, a scanner warning is thrown.</br>
• The scanner warnings are never fatal, though syntactically the tokens returned may cause a parser error.</br>
• For instance, if a string literal has no end quote a warning will be thrown and a quote will be assumed at the end of the line.</br>
## PARSER
• The left recursive from the grammar is removed.</br>
• Type-checking is performed in expressions by returning the types from the expression tree functions and evaluating types for compatibility if an operation is performed.</br>
• Parser resync points are used throughout the compiler to continue parsing if an error is encountered without propagating spurious error messages.</br>
• Note that once a fatal error or any kind is encountered, code will no longer be generated.</br>
## INTERMEDIATE CODE GENERATOR
• Memory and registers for the operation of the program are defned and used as 32-bit integer arrays.</br>
• All non-integer types present in the program are cast as integers for storage in the memory spaces.</br>
• To ensure that pointers are 32-bit and may be cast to integer without issue, the `gcc` compiler fag `-m32` is used.</br>
• Future improvements could be made to "push back" register allocation to the frst register (`R[0]`) at the end of each scope.</br>
## LANGUAGE SYNTAXPROGRAM BODY
the program \<name\> is</br>
define \<declaration\></br>
body</br>
\<statement\></br>
fnish program</br>
## FUNCTION DEFINITION
function \<function name\>(\<datatype\> \<variable\> in, \<datatype\> \<variable\> out) is</br>
\<declaration\></br>
body</br>
\<statement\>finsh functione;</br>
## IF ELSE STATEMENT
if (\<condition\>) then</br>
\<statement\></br>
else</br>
\<statement\></br>
finsh if</br>
## LOOP
for (counter = counter + 1e counter \<= num_loops)<\br>
\<statement\><\br>
fnish for<\br>
## FUNCTION CALL
\<function name\>(\<parameter to pass\>,\<return value\>)
## DATA TYPE
• int – Integer</br>
• bool – Boolean</br>
• str – String</br>
• foat – Float</br>
## FUNCTION
• putstr("Enter 1st Integer:")</br>
• getint(variable)</br>
• putint(result)</br>
• getstr(“enter string”)</br>
• getbool(testbool)</br>
• putbool(testbool)</br>
• getfoat(testfoat)</br>
• putfoat(testfoat)</br>
## GRAMMAR
\<program\> ::= \<program_header\> \<program_body\></br>
\<program_header\> ::= ‘ the’ 'program' \<identifier\> 'is'</br>
\<program_body\> ::= ‘ define’( \<declaration\> ';' )* 'body' ( \<statement\> ';' )* 'finish' 'program' </br>
\<declaration\> ::= [ 'global' ] \<procedure_declaration\> [ 'global' ] \<variable_declaration\></br>
\<variable_declaration\> ::=\<type_mark\> \<identifier\> [ '[' \<array_size\> ']' ] </br>
\<type_mark\> ::= 'int’' | 'float' | 'bool' | 'str' </br>
\<procedure_declaration\> ::= \<procedure_header\> \<procedure_body\> </br>
\<procedure_header\> ::='function' \<identifier\> '(' [ \<parameter_list\> ] ')' ’is’</br>
\<procedure_body\> ::= ( \<declaration\> ';' )* ‘ body' ( \<statement ';' )* 'finish’ 'function' </br>
\<parameter_list\> ::= \<parameter\> ',' \<parameter_list\> |\<parameter\> </br>
\<parameter\> ::= \<variable_declaration\> ( 'in' | 'out' )</br>
\<statement\> ::= \<assignment_statement\> | \<if_statement\> | \<loop_statement\> | \<return_statement\> |
\<procedure_call\> </br>
\<assignment_statement\> ::= \<destination\> '=' \<expression\></br>
\<if_statement\> ::= 'if' '(' \<expression\> ')' 'then' ( \<statement\> ';' )+ [ 'else' ( \<statement\> ';' )+ ]
'finish' 'if'</br>
\<loop_statement\> ::= 'for' '(' \<assignment_statement\> ';' \<expression\> ')' ( \<statement\> ';' )* 'finish' 'for' </br>
\<procedure_call\> ::= \<identifier\> '(' [ \<argument_list\> ] ')'</br>
\<argument_list\> ::= \<expression\> ',' \<argument_list\> |\<expression\> </br>
\<destination\> ::= \<identifier\> [ '[' \<expression\> ']' ] </br>
\<expression\> ::= \<expression\> '&' \<arith_op\> | \<expression\> '|' \<arith_op\> | [ 'not' ] \<arith_op\> </br>
\<arith_op\> ::= \<arith_op\> '+' \<relation\> | \<arith_op\> '-' \<relation\> |\<relation\> </br>
\<relation\> ::= \<relation\> '\<' \<term\> | \<relation\> '\>' \<term\> | \<relation\> '\>=' \<term\> | \<relation\> '\<=' \<term\> |\<relation\> '==' \<term\> |\<relation\> '!=' \<term\> |\<term\> </br>
\<term\> ::= \<term\> '*' \<factor\> | \<term\> '/' \<factor\> | \<factor\> </br>
\<factor\> ::= '(' \<expression\> ')' | [ '-' ] \<name\> | [ '-' ] \<number\> | \<string\> | 'true' | 'false' |</br>
\<name\> ::= \<identifier\> [ '[' \<expression\> ']' ]</br>
\<identifier\> ::= [a-zA-Z][a-zA-Z0-9_]* </br>
\<number\> ::= [0-9][0-9_]*[.[0-9_]*]? </br>
\<string\> ::= "[a-zA-Z0-9 _,;:.']*" </br>
## GUI 
![compiler1](https://user-images.githubusercontent.com/29707542/49634701-85c6d580-fa23-11e8-852b-89079215d67c.png)
![compiler2](https://user-images.githubusercontent.com/29707542/49634708-8b242000-fa23-11e8-9363-0aef06a62514.png)

### STEPS to run the program
$ `sudo apt update`</br>
$ `sudo apt install apache2`</br>
$ `sudo apt-get install python3`<\br>
$ `sudo systemctl stop apache2.service` </br>
$ `sudo systemctl start apache2.service` </br>
$ `sudo systemctl enable apache2.service` </br>
$ `sudo apt install php7.2 libapache2-mod-php7.2 php7.2-common php7.2-mbstring php7.2-xmlrpc php7.2-soap php7.2-gd php7.2-xml php7.2-intl php7.2-mysql php7.2-cli php7.2-zip php7.2-curl`</br>
Copy the HTML, PHP, CSS, input.txt and test.src file in /var/www/html/ and type the localhost/index1.php in browser.</br>
Edit the Path of the file `compiler.py` in index1.php </br>
if the program doesnot work then run $ `sudo chmod 777 *` in /var/www/html/ </br>
if you wish to make RDDS as a command then open the bashrc file(sudo gedit ~/.bashrc) and write the command `alias RDDS ='python3 /home/raghav/Downloads/compiler/2compiler/compiler.py -o OUT'` in this you need to replace the path of compiler.py file.</br>
use the command `RDDS rdds_test/simple_add.src` and `./a.out` to see the output
