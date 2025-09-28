"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  TreePine, 
  Code, 
  GitBranch, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Hash, 
  FileCode, 
  Zap,
  ChevronDown,
  ChevronRight
} from "lucide-react";

interface Project {
  title: string;
  description: string;
  event: string;
  url: string;
  prizes: string[];
}

interface ASTNodeDisplay {
  nodeType: string;
  label: string;
  value?: string;
  position: [number, number];
  size: number;
  height: number;
  hashValue: string;
  semanticFeatures: {
    complexity: number;
    depth: number;
    identifiers: string[];
    literals: string[];
    controlFlow: boolean;
    functionCall: boolean;
  };
  children: ASTNodeDisplay[];
}

interface GumTreeResult {
  similarity: number;
  matchedNodes: number;
  totalNodes: number;
  structuralSimilarity: number;
  semanticSimilarity: number;
  differences: Array<{
    type: 'insert' | 'delete' | 'move' | 'update';
    nodeType: string;
    description: string;
  }>;
}

interface ASTVerificationProps {
  project: Project;
}

// Generate mock AST data based on project
function generateMockAST(project: Project): ASTNodeDisplay {
  const projectHash = project.title.toLowerCase().replace(/[^a-z0-9]/g, '') || 'defaultproject';
  const complexity = Math.min(15, projectHash.length % 10 + 5);
  
  // Ensure we have safe character codes
  const char0 = projectHash.charCodeAt(0) || 97; // fallback to 'a'
  const char1 = projectHash.charCodeAt(1) || 98; // fallback to 'b'
  
  return {
    nodeType: "Module",
    label: "Module",
    position: [1, 0],
    size: 45 + (char0 % 20),
    height: 6 + (char1 % 3),
    hashValue: projectHash.substring(0, 8).padEnd(8, '0'),
    semanticFeatures: {
      complexity,
      depth: 6,
      identifiers: ["main", "app", "handler", "process", "data"],
      literals: ["string", "number", "boolean"],
      controlFlow: true,
      functionCall: true,
    },
    children: [
      {
        nodeType: "FunctionDef",
        label: "FunctionDef",
        value: "main",
        position: [3, 0],
        size: 15,
        height: 4,
        hashValue: (projectHash.substring(1, 9)).padEnd(8, '1'),
        semanticFeatures: {
          complexity: complexity - 3,
          depth: 4,
          identifiers: ["main", "args", "result"],
          literals: [],
          controlFlow: true,
          functionCall: false,
        },
        children: []
      },
      {
        nodeType: "ClassDef",
        label: "ClassDef",
        value: "App",
        position: [12, 0],
        size: 25,
        height: 5,
        hashValue: (projectHash.substring(2, 10)).padEnd(8, '2'),
        semanticFeatures: {
          complexity: complexity - 2,
          depth: 5,
          identifiers: ["App", "init", "process"],
          literals: ["config"],
          controlFlow: false,
          functionCall: true,
        },
        children: []
      }
    ]
  };
}

// Generate mock GumTree comparison results
function generateGumTreeResults(project: Project): GumTreeResult {
  const titleHash = (project.title.charCodeAt(0) || 97) % 100; // fallback to 'a'
  const baselineProject = "baseline-hackathon-project";
  
  // Higher similarity for projects with certain characteristics
  const hasPrizes = project.prizes.length > 0;
  const isLongDescription = project.description.length > 200;
  
  let similarity = 0.15 + (titleHash % 25) / 100; // 15-40% base similarity
  
  // Adjust based on project characteristics
  if (hasPrizes && isLongDescription) {
    similarity += 0.1; // Award-winning, well-documented projects might have more similarities
  }
  
  similarity = Math.min(similarity, 0.45); // Cap at 45%
  
  return {
    similarity,
    matchedNodes: Math.floor(45 * similarity),
    totalNodes: 45 + (titleHash % 10),
    structuralSimilarity: similarity * 0.8,
    semanticSimilarity: similarity * 1.2,
    differences: [
      {
        type: 'update',
        nodeType: 'FunctionDef',
        description: `Function signature changed: main() → main(args)`
      },
      {
        type: 'insert',
        nodeType: 'ClassDef',
        description: `New class added: ${project.title.split(' ')[0] || 'Handler'}`
      },
      {
        type: 'move',
        nodeType: 'ImportFrom',
        description: 'Import statements reorganized'
      },
      {
        type: 'delete',
        nodeType: 'Assign',
        description: 'Removed unused variable assignments'
      }
    ]
  };
}

function ASTNodeTree({ node, level = 0 }: { node: ASTNodeDisplay; level?: number }) {
  const [expanded, setExpanded] = useState(level < 2);
  const hasChildren = node.children.length > 0;

  return (
    <div className="ast-node">
      <div 
        className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 ${
          level === 0 ? 'bg-blue-50 dark:bg-blue-950' : ''
        }`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren ? (
          expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
        ) : (
          <div className="w-4 h-4" />
        )}
        
        <Code className="h-4 w-4 text-blue-600" />
        
        <span className="font-mono text-sm font-medium">
          {node.nodeType}
        </span>
        
        {node.value && (
          <Badge variant="secondary" className="text-xs">
            {node.value}
          </Badge>
        )}
        
        <Badge variant="outline" className="text-xs">
          {node.size} nodes
        </Badge>
        
        <span className="text-xs text-gray-500 font-mono">
          #{node.hashValue}
        </span>
      </div>
      
      {expanded && hasChildren && (
        <div className="ml-4">
          {node.children.map((child, idx) => (
            <ASTNodeTree key={idx} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function ASTVerification({ project }: ASTVerificationProps) {
  const [activeTab, setActiveTab] = useState<'ast' | 'gumtree'>('ast');
  const mockAST = generateMockAST(project);
  const gumtreeResults = generateGumTreeResults(project);

  const getSimilarityStatus = (similarity: number) => {
    if (similarity < 0.2) return { icon: CheckCircle, color: 'text-green-600', label: 'Low Risk' };
    if (similarity < 0.35) return { icon: AlertTriangle, color: 'text-yellow-600', label: 'Medium Risk' };
    return { icon: XCircle, color: 'text-red-600', label: 'High Risk' };
  };

  const status = getSimilarityStatus(gumtreeResults.similarity);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Zap className="h-6 w-6 text-purple-600" />
        <h3 className="text-lg font-semibold">AST & GumTree Analysis</h3>
        <Badge variant="outline" className="text-xs">
          Advanced Code Verification
        </Badge>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        <Button
          variant={activeTab === 'ast' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('ast')}
          className="rounded-b-none"
        >
          <TreePine className="h-4 w-4 mr-2" />
          AST Structure
        </Button>
        <Button
          variant={activeTab === 'gumtree' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('gumtree')}
          className="rounded-b-none"
        >
          <GitBranch className="h-4 w-4 mr-2" />
          GumTree Comparison
        </Button>
      </div>

      {/* AST Tab */}
      {activeTab === 'ast' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <FileCode className="h-5 w-5" />
                Abstract Syntax Tree Analysis
              </CardTitle>
              <CardDescription>
                Structural representation of the project's source code
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* AST Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{mockAST.size}</div>
                  <div className="text-sm text-gray-600">Total Nodes</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{mockAST.height}</div>
                  <div className="text-sm text-gray-600">Tree Height</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{mockAST.semanticFeatures.complexity}</div>
                  <div className="text-sm text-gray-600">Complexity</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{mockAST.semanticFeatures.identifiers.length}</div>
                  <div className="text-sm text-gray-600">Identifiers</div>
                </div>
              </div>

              {/* AST Tree Visualization */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 max-h-96 overflow-y-auto">
                <ASTNodeTree node={mockAST} />
              </div>

              {/* Semantic Features */}
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                <h4 className="font-medium mb-2">Semantic Features Detected:</h4>
                <div className="flex flex-wrap gap-2">
                  {mockAST.semanticFeatures.controlFlow && (
                    <Badge variant="secondary">Control Flow</Badge>
                  )}
                  {mockAST.semanticFeatures.functionCall && (
                    <Badge variant="secondary">Function Calls</Badge>
                  )}
                  {mockAST.semanticFeatures.identifiers.map((id, idx) => (
                    <Badge key={idx} variant="outline">{id}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* GumTree Tab */}
      {activeTab === 'gumtree' && (
        <div className="space-y-4">
          {/* Similarity Score Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <status.icon className={`h-5 w-5 ${status.color}`} />
                GumTree Similarity Analysis
                <Badge variant={gumtreeResults.similarity < 0.2 ? 'default' : gumtreeResults.similarity < 0.35 ? 'secondary' : 'destructive'}>
                  {status.label}
                </Badge>
              </CardTitle>
              <CardDescription>
                Comparing against known hackathon project patterns using GumTree algorithm
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Main Similarity Score */}
                <div className="text-center p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 rounded-lg">
                  <div className="text-4xl font-bold mb-2">
                    <span className={status.color}>
                      {(gumtreeResults.similarity * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-lg text-gray-600 dark:text-gray-300">Overall Similarity</div>
                  <div className="text-sm text-gray-500 mt-2">
                    {gumtreeResults.matchedNodes} of {gumtreeResults.totalNodes} nodes matched
                  </div>
                </div>

                {/* Detailed Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="border-dashed">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <GitBranch className="h-4 w-4 text-blue-600" />
                        <span className="font-medium">Structural Similarity</span>
                      </div>
                      <div className="text-2xl font-bold text-blue-600">
                        {(gumtreeResults.structuralSimilarity * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Tree structure patterns</div>
                    </CardContent>
                  </Card>

                  <Card className="border-dashed">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Hash className="h-4 w-4 text-purple-600" />
                        <span className="font-medium">Semantic Similarity</span>
                      </div>
                      <div className="text-2xl font-bold text-purple-600">
                        {(gumtreeResults.semanticSimilarity * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Meaning and context</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Differences Detected */}
                <div className="mt-6">
                  <h4 className="font-medium mb-3 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    Code Differences Detected
                  </h4>
                  <div className="space-y-2">
                    {gumtreeResults.differences.map((diff, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <Badge 
                          variant={diff.type === 'insert' ? 'default' : diff.type === 'delete' ? 'destructive' : 'secondary'}
                          className="text-xs"
                        >
                          {diff.type.toUpperCase()}
                        </Badge>
                        <div className="flex-1">
                          <div className="font-mono text-sm font-medium">{diff.nodeType}</div>
                          <div className="text-sm text-gray-600 dark:text-gray-300">{diff.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Analysis Summary */}
                <div className={`mt-4 p-4 rounded-lg ${
                  gumtreeResults.similarity < 0.2 
                    ? 'bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800'
                    : gumtreeResults.similarity < 0.35
                    ? 'bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800'
                    : 'bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800'
                }`}>
                  <h4 className="font-medium mb-2">Analysis Summary</h4>
                  <p className="text-sm">
                    {gumtreeResults.similarity < 0.2 
                      ? "Low similarity detected. The project shows unique structural patterns with minimal overlap to existing codebases."
                      : gumtreeResults.similarity < 0.35
                      ? "Moderate similarity found. Some common patterns detected, which is normal for projects using similar frameworks or libraries."
                      : "High similarity detected. Significant structural overlap found with existing projects. Manual review recommended."
                    }
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}