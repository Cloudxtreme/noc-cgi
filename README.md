noc-cgi
======

## ABOUT

Simple CGI script to test network status. See http://noc.1gb.ru/

## INSTALLATION

* Create a web site with CGI support (use any web server you like).
* (optional) Edit `%server_names` hash.
* Install index.cgi into the document root.
* Make sure the script can execute `ping`, `tracepath` and `traceroute`.
