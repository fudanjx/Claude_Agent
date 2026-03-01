---
name: web-research
description: Perform comprehensive web research using search tools. Use when the user asks to research topics, compare information, or gather data from the internet.
keywords: [research, search, web, internet, investigate, study, compare, sources]
---

# Web Research Skill

## Overview

This skill provides a systematic methodology for conducting thorough web research using available search and fetch tools. Follow this approach when users request research, fact-checking, comparisons, or gathering information from the internet.

## When to Use This Skill

Activate this skill when the user requests:
- Research on a topic or subject
- Comparison of multiple sources or viewpoints
- Gathering current information from the web
- Fact-checking claims with authoritative sources
- Understanding trends, news, or developments
- Finding documentation or technical information

## Research Methodology

### 1. Define the Research Question

Before searching, clarify:
- What specific information is needed?
- What is the scope of research?
- Are there time constraints (recent information only)?
- What level of depth is required?

### 2. Search Strategy

Execute searches using the `web_search` tool:

**Multiple Query Approaches:**
- Start with broad queries to understand the landscape
- Follow with specific queries to dive deeper
- Use different phrasings to capture diverse perspectives
- Consider synonyms and related terms

**Search Best Practices:**
- Use 3-5 search queries per research topic
- Vary query structure (questions, keywords, phrases)
- Search for both overview and specific aspects
- Look for recent information and historical context

### 3. Source Evaluation

When reviewing search results:

**Prioritize Authoritative Sources:**
- Academic institutions (.edu)
- Government sources (.gov)
- Official documentation (official project sites)
- Reputable news organizations
- Industry standards bodies

**Source Quality Indicators:**
- Publication date (recent for current topics)
- Author credentials
- Citations and references
- Domain authority

### 4. Content Extraction

Use the `web_fetch` tool to read full content from top sources:
- Fetch 3-5 relevant sources per research question
- Extract key facts, statistics, and quotes
- Note the source URL for each piece of information
- Identify points of agreement and disagreement across sources

### 5. Analysis and Synthesis

Combine findings from multiple sources:
- Identify common themes and patterns
- Note contradictions or controversies
- Distinguish between facts and opinions
- Assess credibility of claims
- Synthesize information into coherent insights

### 6. Citation and Documentation

Always provide proper attribution:
- Include source URLs for all facts and claims
- Note publication dates when relevant
- Indicate when information is from multiple sources
- Flag any uncertainty or conflicting information

## Output Format

Structure research results as:

```markdown
## Research Findings: [Topic]

### Summary
[2-3 paragraph executive summary of key findings]

### Key Points
1. [Finding 1] ([Source URL])
2. [Finding 2] ([Source URL])
3. [Finding 3] ([Source URL])

### Detailed Analysis
[Section 1: Aspect of topic]
- Detail with citation
- Detail with citation

[Section 2: Another aspect]
- Detail with citation
- Detail with citation

### Sources
1. [Source Title] - [URL]
2. [Source Title] - [URL]

### Limitations
- [Any gaps in available information]
- [Conflicting information found]
```

## Best Practices

### Do:
- Cross-reference information across multiple sources
- Provide context for statistics and claims
- Note the date of information when it matters
- Be transparent about limitations or gaps
- Use direct quotes when appropriate
- Link to original sources

### Don't:
- Rely on a single source for important claims
- Present opinions as facts
- Ignore conflicting information
- Omit source citations
- Make claims beyond what sources support
- Use outdated information without noting the date

## Example Workflow

For a request like "Research the benefits of TypeScript":

1. **Search Phase:**
   - "TypeScript benefits advantages"
   - "TypeScript vs JavaScript comparison"
   - "TypeScript adoption statistics"
   - "TypeScript developer experience"

2. **Fetch Phase:**
   - TypeScript official documentation
   - Developer surveys and reports
   - Technical blog posts from reputable sources
   - Industry case studies

3. **Analysis Phase:**
   - Compile list of commonly cited benefits
   - Note statistics on adoption and satisfaction
   - Identify potential drawbacks or trade-offs
   - Synthesize into coherent overview

4. **Output Phase:**
   - Present findings with clear structure
   - Cite all sources
   - Provide balanced perspective
   - Note any limitations in research

## Quality Checklist

Before completing research, verify:
- [ ] Used multiple search queries
- [ ] Consulted 3+ authoritative sources
- [ ] Cross-referenced key claims
- [ ] Provided source URLs for all facts
- [ ] Noted publication dates where relevant
- [ ] Presented information objectively
- [ ] Acknowledged any limitations or gaps
- [ ] Structured information clearly

## Notes

- Always use available tools (`web_search`, `web_fetch`)
- Adapt depth of research to user's needs
- Be efficient - don't over-research simple questions
- When information conflicts, present both perspectives
- For technical topics, prioritize official documentation
