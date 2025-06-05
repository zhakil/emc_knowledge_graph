


export interface TestResult {
    id: string;














  testId: string;
  testName: string;
    standard: string;









  status: 'Pass' | 'Fail' | 'Warning' | 'In Progress';
  date: string;
  frequencyRange?: string;
  testEngineer: string;
  equipmentUsed?: string[];
  complianceMargin?: number;
    issues?: string;
    position?: { x: number; y: number };
}

export interface TestDependencyGraph {
  tests: {
    id: string;
    name: string;
    standard: string;
    frequencyRange: string;
    position?: { x: number; y: number };
  }[];



  equipment: {
    id: string;
    name: string;
    model: string;
    calibrationDate: string;
    position?: { x: number; y: number };
  }[];







  requirements: {
    id: string;
    standard: string;
    section: string;
    position?: { x: number; y: number };
  }[];
  results: TestResult[];
  dependencies: {
    source: string;
    target: string;
  }[];
  requirementsLinks: {
    testId: string;
    reqId: string;
  }[];
  resultLinks: {
    testId: string;
    resultId: string;
  }[];
}