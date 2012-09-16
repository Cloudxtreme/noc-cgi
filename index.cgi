#!/usr/bin/perl -w
use strict;
use CGI qw/:standard/;
use IO::Handle;

autoflush STDOUT 1;
autoflush STDERR 1;
open(STDERR, ">&STDOUT");

my %server_names = (
    "dc0.noc.1gb.ru"        => "1Gb.ru Moscow RTcomm/Stack (dc0)",
    "dc1.noc.1gb.ru"        => "1Gb.ru Moscow RTcomm/M10 (dc1)",
    "noc.1gb.ua"            => "1Gb.ua Kiev TOPNET.ua",
    "frankfurt-noc.1gb.ru"  => "1Gb.ru Frankfurt am Main (Germany)",
    "hetzner-noc.1gb.ru"    => "Hetzner (Germany)",
);
my $remote = $ENV{HTTP_X_FORWARDED_FOR} || $ENV{REMOTE_ADDR} || die;
my $server = $ENV{SERVER_NAME} or die;
my $desc = ( $server_names{$server} ||= "unknown ($server)" );
my $title = "1Gb.ru noc: $desc";
my $query = param('q') || $remote;
my $uri = $ENV{REQUEST_URI} || "";

print
    header,
    "<html><head><title>$title</title></head><body>\n",
    h1($title);
print "<script>
function whois_()
{
    window.open( 'http://www.nic.ru/whois/?query=' + document.getElementById('q').value );
    return false;
}

function clear_()
{
    window.location = 'http://$server';
    return false;
}
</script>\n";

chomp $query;
$query =~ s/^\s*//;
$query =~ s/\s*$//;
unless( $query =~ /^\w[\w\.\-]+\w$/ ) {
    print "Bad query: $query";
    $query = $remote;
}
my $query_is_ipv4 = ( $query =~ /^\d+\.\d+\.\d+\.\d+$/ );

print ul(
    li( {-type=>'disc'}, [
        map {
            $server eq $_ ?
                b($desc) :
                a( { -href => "http://$_/$uri" }, $server_names{$_} )
        } sort keys %server_names
    ] ),
), "\n";
print join "\n",
    start_form(-method=>"get", -name => 'main', -action=>"http://$server/"),
    table( {},
        Tr( {-align=>'left'},
            td("Your IP:"),
            td($remote),
        ),
        Tr( {-align=>'left'},
            td("IP or domain:"),
            td(
                textfield( -name => 'q', -id => 'q', -value => $query )
            ),
        ),
    ),
    submit( -name=>'ping' ),
    submit( -name=>'tracepath' ),
    submit( -name=>'traceroute' ),
    submit( -name=>'dig' ),
    end_form,
    "<form name='whois' onsubmit='return whois_()'><input type='submit' name='whois' value='whois' /></form>\n",
    "<form name='clear' onsubmit='return clear_()'><input type='submit' name='clear' value='clear' /></form>\n",
    hr;


print h3("Resolved:");
my $hostout = `host $query`;
$hostout =~ s/\b(\w[\w\-]+\.[\w\.\-]+\w)(\.?)$/<a href="\/?q=$1">$1<\/a>$2/g;
$hostout =~ s/\b(\w[\w\-]+\.[\w\.\-]+\w)(\.?\s)/<a href="\/?q=$1">$1<\/a>$2/g;
print pre($hostout), hr;

sub run(@) {
    print h3("@_"), "\n<pre>";
    system(@_);
    print "</pre>\n<hr />\n";
}

if( param('ping') ) {
    run( "ping", "-c", 5, $query );
} elsif( param('tracepath') ) {
    run( "tracepath", $query );
} elsif( param('traceroute') ) {
    run( "traceroute", $query );
} elsif( param('env') ) {
    run( "env" );
} elsif( param('dig') ) {
    if( $query_is_ipv4 ) {
        run( "dig", "+trace", "-x", $query );
    } else {
        run( "dig", "+trace", $query );
    }
}
