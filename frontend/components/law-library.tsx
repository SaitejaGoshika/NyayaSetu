"use client";

import { useMemo, useState } from "react";
import { BookOpen, ExternalLink, Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const laws = [
  { title: "Constitution of India", year: "1950", area: "Constitutional", summary: "The framework for government, fundamental rights, and the structure of courts in India.", terms: "rights courts government" },
  { title: "Bharatiya Nyaya Sanhita", year: "2023", area: "Criminal", summary: "The principal statute defining offences and punishments, in force from 1 July 2024.", terms: "offences criminal punishment ipc" },
  { title: "Bharatiya Nagarik Suraksha Sanhita", year: "2023", area: "Criminal", summary: "The principal statute on criminal procedure, investigation, and trial, in force from 1 July 2024.", terms: "criminal procedure police trial crpc" },
  { title: "Bharatiya Sakshya Adhiniyam", year: "2023", area: "Evidence", summary: "Rules on evidence in judicial proceedings, including electronic records, in force from 1 July 2024.", terms: "evidence electronic records proof evidence act" },
  { title: "Code of Civil Procedure", year: "1908", area: "Civil", summary: "Procedural framework for civil suits and proceedings, subject to amendments and applicable rules.", terms: "civil suit procedure cpc" },
  { title: "Indian Contract Act", year: "1872", area: "Civil", summary: "General principles governing contracts, obligations, and certain forms of indemnity and guarantee.", terms: "contract agreement breach indemnity" },
  { title: "Limitation Act", year: "1963", area: "Civil", summary: "Provides limitation periods for many proceedings. The applicable period and rules depend on the claim and facts.", terms: "limitation time limit deadline delay" },
  { title: "Specific Relief Act", year: "1963", area: "Civil", summary: "Concerns specific civil remedies, including certain forms of specific performance and injunctions.", terms: "specific performance injunction remedy" },
  { title: "Transfer of Property Act", year: "1882", area: "Property", summary: "Addresses certain transfers of property, including sale, mortgage, lease, exchange, and gifts.", terms: "property land sale mortgage lease gift" },
  { title: "Registration Act", year: "1908", area: "Property", summary: "Provides for registration of specified documents and related registration procedures.", terms: "property registration deed document" },
  { title: "Negotiable Instruments Act", year: "1881", area: "Commercial", summary: "Governs negotiable instruments, including provisions concerning certain cheque dishonour cases.", terms: "cheque bounce dishonour business payment" },
  { title: "Micro, Small and Medium Enterprises Development Act", year: "2006", area: "Commercial", summary: "Includes provisions concerning delayed payments to micro and small enterprises and dispute facilitation.", terms: "msme delayed payment samadhaan enterprise" },
  { title: "Commercial Courts Act", year: "2015", area: "Commercial", summary: "Framework for designated commercial courts and specified commercial disputes.", terms: "commercial business court mediation" },
  { title: "Arbitration and Conciliation Act", year: "1996", area: "Dispute resolution", summary: "Framework for arbitration and conciliation. Arbitration generally depends on an applicable arbitration agreement.", terms: "arbitration conciliation mediation agreement" },
  { title: "Mediation Act", year: "2023", area: "Dispute resolution", summary: "Provides a statutory framework for mediation. Commencement and application of provisions should be checked in current official notifications.", terms: "mediation settlement dispute resolution" },
  { title: "Consumer Protection Act", year: "2019", area: "Consumer", summary: "Consumer rights and the framework for consumer commissions and dispute resolution.", terms: "consumer complaint goods services" },
  { title: "Legal Services Authorities Act", year: "1987", area: "Access to justice", summary: "Framework for legal services authorities and Lok Adalats, including eligibility and settlement requirements.", terms: "legal aid lok adalat settlement free lawyer" },
  { title: "Protection of Women from Domestic Violence Act", year: "2005", area: "Family and safety", summary: "Provides civil-law protections and remedies concerning domestic violence. Seek urgent qualified help if anyone is in danger.", terms: "domestic violence protection women family" },
  { title: "Hindu Marriage Act", year: "1955", area: "Family", summary: "Addresses specified aspects of marriage and matrimonial relief for persons to whom the Act applies.", terms: "marriage divorce family matrimonial" },
  { title: "Special Marriage Act", year: "1954", area: "Family", summary: "Provides a civil form of marriage and addresses related matrimonial matters for persons to whom the Act applies.", terms: "civil marriage interfaith family" },
  { title: "Hindu Succession Act", year: "1956", area: "Family and property", summary: "Addresses intestate succession for persons to whom the Act applies, subject to its provisions and amendments.", terms: "inheritance succession property family" },
  { title: "Information Technology Act", year: "2000", area: "Digital", summary: "Addresses specified legal issues concerning electronic records, electronic signatures, and certain cyber offences.", terms: "cyber online electronic record digital" },
  { title: "Right to Information Act", year: "2005", area: "Public services", summary: "Provides a process to request information from public authorities, subject to statutory exemptions and procedure.", terms: "rti government information public authority" },
  { title: "Rights of Persons with Disabilities Act", year: "2016", area: "Equality and access", summary: "Addresses rights and entitlements of persons with disabilities, including specified accessibility and non-discrimination provisions.", terms: "disability accessibility equality reasonable accommodation" },
  { title: "Protection of Children from Sexual Offences Act", year: "2012", area: "Child protection", summary: "Provides a child-protection framework for specified sexual offences and related procedures.", terms: "pocso child protection safety" },
  { title: "Juvenile Justice (Care and Protection of Children) Act", year: "2015", area: "Child protection", summary: "Addresses care, protection, and rehabilitation of children, including procedures for children in conflict with law.", terms: "juvenile child care protection rehabilitation" },
  { title: "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act", year: "1989", area: "Equality and safety", summary: "Provides a framework addressing specified offences and protections for members of Scheduled Castes and Scheduled Tribes.", terms: "sc st atrocity protection equality" },
  { title: "Motor Vehicles Act", year: "1988", area: "Transport", summary: "Addresses motor vehicle regulation, licensing, insurance, and specified compensation processes.", terms: "road accident vehicle insurance compensation" },
  { title: "Real Estate (Regulation and Development) Act", year: "2016", area: "Property", summary: "Provides a framework for regulation of the real estate sector and matters assigned to state and union territory authorities.", terms: "rera housing builder flat property" },
];

const legalResources = [
  { title: "eCourts Services", summary: "Use official eCourts services to look for case information and citizen-facing court services. Availability and displayed data can vary by court.", href: "https://services.ecourts.gov.in/ecourtindia_v6/", label: "Open eCourts Services", terms: "case status court case cnr district court" },
  { title: "eCourts national portal", summary: "Learn about the eCourts project and find links to High Court and District Court websites.", href: "https://ecourts.gov.in/ecourts2.0/", label: "Visit eCourts portal", terms: "high court district court judiciary" },
  { title: "National Legal Services Authority (NALSA)", summary: "Find information about legal services authorities, legal aid, Lok Adalats, and access-to-justice programmes. Eligibility for legal aid is governed by law.", href: "https://nalsa.gov.in/", label: "Visit NALSA", terms: "legal aid free lawyer lok adalat settlement" },
  { title: "Tele-Law", summary: "Explore the Department of Justice's Tele-Law programme information and available access-to-legal-advice routes.", href: "https://tele-law.in/", label: "Visit Tele-Law", terms: "legal advice online justice department" },
  { title: "India Code", summary: "Search the official Government of India repository of central Acts and legislation. Check amendments and commencement details in the official text.", href: "https://www.indiacode.nic.in/", label: "Search India Code", terms: "central acts legislation law official text" },
  { title: "National Consumer Helpline", summary: "Find official consumer grievance information and contact options before choosing a formal complaint route.", href: "https://consumerhelpline.gov.in/", label: "Visit National Consumer Helpline", terms: "consumer complaint grievance help" },
];

const areas = ["All topics", ...Array.from(new Set(laws.map((law) => law.area)))];
const INDIA_CODE_URL = "https://www.indiacode.nic.in/";

export function LawLibrary() {
  const [query, setQuery] = useState("");
  const [area, setArea] = useState("All topics");
  const [view, setView] = useState<"acts" | "services">("acts");
  const filteredLaws = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return laws.filter((law) => (area === "All topics" || law.area === area)
      && (!normalizedQuery || `${law.title} ${law.year} ${law.area} ${law.summary} ${law.terms}`.toLowerCase().includes(normalizedQuery)));
  }, [area, query]);
  const filteredResources = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return legalResources.filter((resource) => !normalizedQuery
      || `${resource.title} ${resource.summary} ${resource.terms}`.toLowerCase().includes(normalizedQuery));
  }, [query]);

  return (
    <section className="rise-in mx-auto max-w-6xl">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Public legal information</p>
          <h2 className="mt-1 text-2xl font-semibold">Browse the law library</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">Plain-language introductions to Indian central Acts, plus official court and legal-help resources. Use the official source and qualified legal advice to understand how a law applies to your facts.</p>
        </div>
        <Badge variant="neutral"><BookOpen size={13} />{view === "acts" ? `${filteredLaws.length} Acts` : `${filteredResources.length} resources`}</Badge>
      </div>

      <div aria-label="Library section" className="mb-4 flex flex-wrap gap-2" role="group">
        <button aria-pressed={view === "acts"} className={`min-h-9 rounded-md px-3 text-xs font-semibold ${view === "acts" ? "bg-green text-white" : "border border-line bg-white text-foreground hover:bg-mint"}`} onClick={() => setView("acts")} type="button">Acts &amp; laws</button>
        <button aria-pressed={view === "services"} className={`min-h-9 rounded-md px-3 text-xs font-semibold ${view === "services" ? "bg-green text-white" : "border border-line bg-white text-foreground hover:bg-mint"}`} onClick={() => setView("services")} type="button">Court &amp; public help</button>
      </div>

      <Card className="mb-5 p-4">
        <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_220px]">
          <label className="relative block" htmlFor="law-search">
            <Search aria-hidden className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={15} />
            <input aria-label={view === "acts" ? "Search laws or topics" : "Search court and public help"} className="h-10 w-full rounded-md border border-line bg-white pl-9 pr-3 text-sm outline-none focus:border-green focus:ring-2 focus:ring-green/15" id="law-search" onChange={(event) => setQuery(event.target.value)} placeholder={view === "acts" ? "Search laws or topics" : "Search court and public help"} type="search" value={query} />
          </label>
          {view === "acts" ? (
            <>
              <label className="sr-only" htmlFor="law-area">Filter by topic</label>
              <select className="h-10 rounded-md border border-line bg-white px-3 text-sm outline-none focus:border-green focus:ring-2 focus:ring-green/15" id="law-area" onChange={(event) => setArea(event.target.value)} value={area}>
                {areas.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </>
          ) : <p className="self-center text-xs text-muted">Official government and court services</p>}
        </div>
      </Card>

      {view === "acts" && (filteredLaws.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredLaws.map((law) => (
            <Card className="flex flex-col p-5" key={law.title}>
              <div className="mb-3 flex items-start justify-between gap-3"><div className="grid size-9 shrink-0 place-items-center rounded-md bg-mint text-green"><BookOpen size={16} /></div><Badge variant="neutral">{law.area}</Badge></div>
              <h3 className="text-sm font-semibold leading-5">{law.title}, {law.year}</h3>
              <p className="mt-2 flex-1 text-xs leading-5 text-muted">{law.summary}</p>
              <a aria-label={`Search official text for ${law.title} on India Code`} className="mt-4 inline-flex min-h-9 items-center gap-2 border-t border-line pt-3 text-xs font-semibold text-green hover:text-green-dark" href={INDIA_CODE_URL} rel="noreferrer" target="_blank">
                Find official text on India Code<ExternalLink aria-hidden size={13} />
              </a>
            </Card>
          ))}
        </div>
      ) : <NoMatches />)}

      {view === "services" && (filteredResources.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredResources.map((resource) => (
            <Card className="flex flex-col p-5" key={resource.title}>
              <div className="mb-3 grid size-9 place-items-center rounded-md bg-mint text-green"><ExternalLink size={16} /></div>
              <h3 className="text-sm font-semibold leading-5">{resource.title}</h3>
              <p className="mt-2 flex-1 text-xs leading-5 text-muted">{resource.summary}</p>
              <a className="mt-4 inline-flex min-h-9 items-center gap-2 border-t border-line pt-3 text-xs font-semibold text-green hover:text-green-dark" href={resource.href} rel="noreferrer" target="_blank">
                {resource.label}<ExternalLink aria-hidden size={13} />
              </a>
            </Card>
          ))}
        </div>
      ) : <NoMatches />)}

      <p className="mt-5 rounded-md border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-950">Educational starting points only. This library is not a complete or continuously updated legal database. Laws may be amended, interpreted by courts, or subject to state-specific rules. Verify current official texts, notifications, and local procedures. This is not legal advice.</p>
    </section>
  );
}

function NoMatches() {
  return (
    <Card className="grid min-h-36 place-items-center p-6 text-center">
      <div><Search className="mx-auto mb-2 text-muted" size={19} /><p className="text-sm font-medium">No matching resources</p><p className="mt-1 text-xs text-muted">Try another title, topic, or filter.</p></div>
    </Card>
  );
}
