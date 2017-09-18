#!/usr/bin/tclsh

package require http
package require csv

set download_list {"http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
	"http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download"
	"http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download"}

set fid_company_list [open "company.list" "w"]
set fid_symbol_list [open "symbol.list" "w"]

puts $fid_symbol_list "Symbol"

foreach query $download_list {
	# puts $query
	set url [http::geturl $query]
	puts $fid_company_list [http::data $url]
	set i 0
	foreach res [split [string trim [http::data $url]] "\r\n"] {
		if {$res != ""} {
			# puts $res
			set fields [::csv::split $res]
			if {$i != 0} {
				puts $fid_symbol_list [lindex $fields 0]
			}
			incr i
		}
	}
}

flush $fid_symbol_list
flush $fid_company_list
close $fid_symbol_list
close $fid_company_list

exit 0

