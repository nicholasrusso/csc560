select * from person;
select * from legislator;
select * from term;
select * from bill;
select * from billdiscussion;
select * from utterance;

select * from person limit 100;
select * from legislator limit 100;
select * from term limit 100;
select * from bill limit 100;
select * from billdiscussion limit 100;
select * from utterance limit 100;

select * from person where person.first like 'A%';
select * from person where person.first like 'B%';
select * from person where person.first like 'C%';
select * from person where person.first like 'D%';
select * from person where person.first like 'E%';
select * from person where person.first like 'F%';
select * from person where person.first like 'G%';
select * from person where person.first like 'H%';
select * from person where person.first like 'I%';
select * from person where person.first like 'J%';
select * from person where person.first like 'K%';
select * from person where person.first like 'L%';
select * from person where person.first like 'M%';
select * from person where person.first like 'N%';
select * from person where person.first like 'O%';
select * from person where person.first like 'P%';
select * from person where person.first like 'Q%';
select * from person where person.first like 'R%';
select * from person where person.first like 'S%';
select * from person where person.first like 'T%';
select * from person where person.first like 'U%';
select * from person where person.first like 'V%';
select * from person where person.first like 'W%';
select * from person where person.first like 'X%';
select * from person where person.first like 'Y%';
select * from person where person.first like 'Z%';

select * from person where person.last like 'A%';
select * from person where person.last like 'B%';
select * from person where person.last like 'C%';
select * from person where person.last like 'D%';
select * from person where person.last like 'E%';
select * from person where person.last like 'F%';
select * from person where person.last like 'G%';
select * from person where person.last like 'H%';
select * from person where person.last like 'I%';
select * from person where person.last like 'J%';
select * from person where person.last like 'K%';
select * from person where person.last like 'L%';
select * from person where person.last like 'M%';
select * from person where person.last like 'N%';
select * from person where person.last like 'O%';
select * from person where person.last like 'P%';
select * from person where person.last like 'Q%';
select * from person where person.last like 'R%';
select * from person where person.last like 'S%';
select * from person where person.last like 'T%';
select * from person where person.last like 'U%';
select * from person where person.last like 'V%';
select * from person where person.last like 'W%';
select * from person where person.last like 'X%';
select * from person where person.last like 'Y%';
select * from person where person.last like 'Z%';

select * from legislator where legislator.twitter_handle is not null;
select legislator.state, count(*) from legislator group by legislator.state;

select term.state, count(*) from term group by term.state;
select term.party, count(*) from term group by term.party;
select term.state, term.party, count(*) from term group by term.state, term.party order by term.state;

select * from hearing where hearing.date > '2017-04-10';
select * from hearing where hearing.type is not null and type = 'Budget';
select * from hearing where hearing.type is not null and type = 'Informational';


select * from bill join billdiscussion on bill.bid = billdiscussion.bid;
select * from hearing join billdiscussion on hearing.hid = billdiscussion.hid;

select * from hearing join billdiscussion on hearing.hid = billdiscussion.hid where hearing.session_year = 2017;

select * from hearing join billdiscussion on hearing.hid = billdiscussion.hid
join bill on bill.bid = billdiscussion.bid
where hearing.session_year = 2017;

select * from person join term on person.pid = term.pid where person.first like 'A%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'B%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'C%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'D%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'E%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'F%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'G%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'H%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'I%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'J%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'K%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'L%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'M%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'N%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'O%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'P%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'Q%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'R%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'S%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'T%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'U%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'V%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'W%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'X%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'Y%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.first like 'Z%' and term.current_term = 1;

select * from person join term on person.pid = term.pid where person.last like 'A%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'B%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'C%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'D%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'E%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'F%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'G%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'H%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'I%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'J%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'K%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'L%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'M%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'N%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'O%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'P%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'Q%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'R%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'S%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'T%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'U%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'V%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'W%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'X%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'Y%' and term.current_term = 1;
select * from person join term on person.pid = term.pid where person.last like 'Z%' and term.current_term = 1;

select * from utterance join person on utterance.pid = person.pid;
select * from utterance join person on utterance.pid = person.pid limit 100;

select * from utterance join billdiscussion on utterance.did = billdiscussion.did;
select * from utterance join billdiscussion on utterance.did = billdiscussion.did limit 100;

select * from utterance join billdiscussion on utterance.did = billdiscussion.did
join bill on billdiscussion.bid = bill.bid
join hearing on billdiscussion.hid = hearing.hid
join person on utterance.pid = person.pid;

select * from utterance join billdiscussion on utterance.did = billdiscussion.did
join bill on billdiscussion.bid = bill.bid
join hearing on billdiscussion.hid = hearing.hid
join person on utterance.pid = person.pid limit 100;

select person.pid, person.first, person.last, count(*)
from utterance join person on utterance.pid = person.pid
group by person.pid;

select term.house, count(*)
from utterance join term on utterance.pid = term.pid
group by term.house;


select term.state, term.house, count(*)
from utterance join term on utterance.pid = term.pid
group by term.state, term.house;

select term.state, term.house, term.party, count(*)
from utterance join term on utterance.pid = term.pid
group by term.state, term.house, term.party;

select term.party, count(*)
from utterance, term
where utterance.pid = term.pid
group by term.party;

select term.state, count(*)
from utterance, term
where utterance.pid = term.pid
group by term.state;

select person.first, person.last, term.state, count(*)
from person join term on person.pid = term.pid
join utterance on person.pid = utterance.pid
group by person.pid;

select person.first, person.last, count(*)
from person join term on person.pid = term.pid
group by person.pid;

select person.first, person.last, term.district, term.state, term.house, count(*)
from person join term on person.pid = term.pid
group by term.state, term.house, term.district, person.pid;

select * from bill where bill.status like "%et%";

select person.pid, person.first, person.last, count(*)
from billdiscussion join bill on billdiscussion.bid = bill.bid
join utterance on utterance.did = billdiscussion.did
join person on person.pid = utterance.pid
where bill.status = "Died"
group by person.pid;

select person.pid, person.first, person.last, count(*)
from billdiscussion join bill on billdiscussion.bid = bill.bid
join utterance on utterance.did = billdiscussion.did
join person on person.pid = utterance.pid
where bill.status = "Chaptered"
group by person.pid;

select person.pid, person.first, person.last, count(*)
from billdiscussion join bill on billdiscussion.bid = bill.bid
join utterance on utterance.did = billdiscussion.did
join person on person.pid = utterance.pid
where bill.status = "Vetoed"
group by person.pid;

select bill.type, count(*)
from billdiscussion join bill on billdiscussion.bid = bill.bid
join utterance on utterance.did = billdiscussion.did
group by bill.type;
