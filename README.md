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
