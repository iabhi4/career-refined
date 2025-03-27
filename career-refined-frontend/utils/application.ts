// utils/application.ts


export interface ProcessedKeyword {
    keyword: string;
    frequency: number;
    inResume: boolean;
  }
  
  function escapeRegExp(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }
  
  export function computeKeywordFrequency(
    extractedKeywords: string[],
    jobDescription: string
  ): Record<string, number> {
    const freqMap: Record<string, number> = {};
    const lowerDesc = jobDescription.toLowerCase();
  
    extractedKeywords.forEach((kw) => {
      freqMap[kw] = 0; // initialize
      const lowerKw = kw.toLowerCase();
  
      // Naive substring search to count occurrences
      let startIndex = 0;
      while (true) {
        const foundIndex = lowerDesc.indexOf(lowerKw, startIndex);
        if (foundIndex === -1) break;
        freqMap[kw] += 1;
        startIndex = foundIndex + lowerKw.length;
      }
    });
  
    return freqMap;
  }
  
  /**
   * Updated getProcessedKeywords to check if the extractedKeywords
   * is directly an array or an object containing the array under a key.
   */
  export function getProcessedKeywords(
    extractedKeywordsInput: any,
    matchedKeywords: string[],
    jobDescription: string
  ): ProcessedKeyword[] {
    let extractedKeywords: string[] = [];
  
    if (Array.isArray(extractedKeywordsInput)) {
      extractedKeywords = extractedKeywordsInput;
    } else if (
      typeof extractedKeywordsInput === "object" &&
      extractedKeywordsInput !== null &&
      Array.isArray(extractedKeywordsInput.technical_keywords)
    ) {
      extractedKeywords = extractedKeywordsInput.technical_keywords;
    } else {
      console.error("Unexpected structure for extractedKeywords:", extractedKeywordsInput);
    }
  
    const freqMap = computeKeywordFrequency(extractedKeywords, jobDescription);
  
    return extractedKeywords.map((kw) => ({
      keyword: kw,
      frequency: freqMap[kw] || 0,
      inResume: matchedKeywords
        .map((m) => m.toLowerCase())
        .includes(kw.toLowerCase()),
    }));
  }
  
  export function highlightJobDescription(
    jobDescription: string,
    processedKeywords: ProcessedKeyword[]
  ): string {
    let highlighted = jobDescription;
    processedKeywords.forEach(({ keyword, inResume }) => {
      const colorClass = inResume ? "bg-green-200" : "bg-yellow-200";
      const regex = new RegExp(`\\b(${escapeRegExp(keyword)})\\b`, "gi");
      highlighted = highlighted.replace(
        regex,
        `<span class="${colorClass} px-1 rounded">$1</span>`
      );
    });
    return highlighted;
  }  

  export function getMatchedKeywords(
    missingKeywords: string[],
    extractedKeywords: string[]
  ): number {
    // Calculate the count of matched keywords
    const matchedCount = extractedKeywords.filter(kw => !missingKeywords.includes(kw)).length;

    return matchedCount;
  }


  export function mergeDeep(oldData: any, newData: any): any {
    const merged: any = {};
    const keys = new Set([
      ...Object.keys(oldData || {}),
      ...Object.keys(newData || {})
    ]);
    for (const key of keys) {
      if (newData[key] === undefined) {
        merged[key] = oldData[key];
      } else if (
        typeof newData[key] === "object" &&
        newData[key] !== null &&
        !Array.isArray(newData[key])
      ) {
        merged[key] = mergeDeep(oldData[key], newData[key]);
      } else {
        merged[key] = newData[key];
      }
    }
    return merged;
  }



  export interface SkillsCategories {
    languages: string[];
    frameworks: string[];
    developerTools: string[];
    cloudTechnologies: string[];
    dbsApplications: string[];
    otherSkillsAndTools: string[];
  }
  
  export function categorizeSkills(skills: string[]): SkillsCategories {
    // Exhaustive default lists for each category.
    const defaultCategories: SkillsCategories = {
      languages: [
        "java", "python", "c", "c++", "c/c++", "javascript", "typescript",
        "html", "css", "sql", "r", "scala", "swift", "objective-c", "kotlin",
        "perl", "ruby", "go", "rust", "dart", "matlab", "julia", "groovy",
        "vb.net", "f#"
      ],
      frameworks: [
        "springboot", "spring mvc", "django", "flask", "express", "laravel",
        "ruby on rails", "react", "angular", "vue", "svelte", "ember", "backbone",
        "node.js", "jquery", "next.js", "nuxt.js", "gatsby", "fastapi", "flutter",
        "asp.net", ".net", "meteor", "redux", "mobx", "polymer", "bootstrap",
        "tailwind", "material-ui", "ant design", "electron", "capacitor"
      ],
      developerTools: [
        "git", "github", "gitlab", "bitbucket", "vs code", "intellij", "pycharm",
        "eclipse", "sublime text", "webstorm", "docker", "postman", "fiddler",
        "jenkins", "travis ci", "circleci", "visual studio", "xcode", "slack",
        "jira", "confluence", "notion", "sourcetree", "npm", "yarn", "webpack",
        "rollup", "babel", "chrome devtools", "vim", "emacs", "terminal", "deno"
      ],
      cloudTechnologies: [
        "aws ec2", "aws rds", "aws s3", "aws lambda", "aws ses", "aws cloudfront",
        "aws elastic beanstalk", "aws dynamodb", "aws cognito", "azure",
        "azure devops", "google cloud platform", "gcp", "heroku", "digitalocean",
        "kubernetes", "docker", "terraform", "ansible", "chef", "puppet",
        "openstack", "vmware", "cloudflare"
      ],
      dbsApplications: [
        "jdbc", "mongodb", "redis", "postgresql", "mysql", "mariadb", "oracle",
        "sql server", "cassandra", "couchdb", "firebase", "neo4j", "dynamodb",
        "elasticsearch", "influxdb", "clickhouse", "snowflake", "hive", "presto"
      ],
      otherSkillsAndTools: [
        "object-oriented programming", "design patterns", "data structures", "algorithms",
        "system design", "microservices", "rest api", "graphql", "soap", "agile methodologies",
        "scrum", "kanban", "tdd", "bdd", "unit testing", "integration testing",
        "performance testing", "load testing", "automation testing", "ci/cd", "docker-compose",
        "monitoring", "logging", "prometheus", "grafana", "elk stack", "security best practices",
        "penetration testing", "debugging", "code review", "pair programming", "version control",
        "devops", "sdlc", "communication", "leadership", "project management", "cloud computing",
        "virtualization", "machine learning", "deep learning", "natural language processing",
        "computer vision", "data analysis", "statistics", "data visualization", "big data",
        "spark", "hadoop", "airflow", "mlops", "research", "innovation", "problem solving",
        "continuous improvement"
      ],
    };
  
    // Prepare an object to collect the user-provided skills by category.
    const userCategorized: SkillsCategories = {
      languages: [],
      frameworks: [],
      developerTools: [],
      cloudTechnologies: [],
      dbsApplications: [],
      otherSkillsAndTools: [],
    };
  
    // Normalize the incoming skills.
    const normalizedSkills = skills.map((skill) => skill.toLowerCase().trim());
  
    // For each normalized skill, check if it exactly matches any default in each category.
    normalizedSkills.forEach((skill) => {
      let matched = false;
      for (const category in defaultCategories) {
        const catKey = category as keyof SkillsCategories;
        if (defaultCategories[catKey].includes(skill)) {
          userCategorized[catKey].push(skill);
          matched = true;
          break;
        }
      }
      // If no default category matched, add it to otherSkillsAndTools.
      if (!matched) {
        userCategorized.otherSkillsAndTools.push(skill);
      }
    });
  
    // Merge defaults and user-provided skills for each category (remove duplicates).
    const mergedResult: SkillsCategories = {} as SkillsCategories;
    for (const category in defaultCategories) {
      const catKey = category as keyof SkillsCategories;
      mergedResult[catKey] = Array.from(
        new Set([...defaultCategories[catKey], ...userCategorized[catKey]])
      );
    }
  
    return mergedResult;
  }