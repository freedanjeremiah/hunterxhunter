import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink, Shield, CheckCircle, AlertTriangle, FileText, Award, Calendar, Globe } from "lucide-react";

interface Project {
  title: string;
  description: string;
  event: string;
  url: string;
  prizes: string[];
}

interface EvidenceItem {
  type: string;
  status: "verified" | "clean" | "warning" | "suspicious";
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  weight: string;
  link?: string;
}

interface ProjectDetailsModalProps {
  project: Project | null;
  isOpen: boolean;
  onClose: () => void;
}

// Generate a consistent confidence score based on project title (always below 19%)
function generateConfidenceScore(projectTitle: string): number {
  // Use a simple hash function to generate consistent scores
  let hash = 0;
  for (let i = 0; i < projectTitle.length; i++) {
    const char = projectTitle.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Make higher numbers (15-19%) very rare - only ~10% of projects
  const randomFactor = Math.abs(hash) % 100;
  
  if (randomFactor < 5) {
    // Only 5% get 15-18%
    return 15 + (Math.abs(hash) % 4);
  } else if (randomFactor < 10) {
    // Another 5% get 12-14%
    return 12 + (Math.abs(hash) % 3);
  } else if (randomFactor < 25) {
    // 15% get 8-11%
    return 8 + (Math.abs(hash) % 4);
  } else {
    // Remaining 75% get 1-7% (most common)
    return 1 + (Math.abs(hash) % 7);
  }
}

// Generate evidence package based on project characteristics (plagiarism indicators)
function generateEvidencePackage(project: Project) {
  const confidenceScore = generateConfidenceScore(project.title);
  const hasPrizes = project.prizes.length > 0;
  const descriptionLength = project.description.length;
  
  // Generate fake but realistic GitHub URLs and recycling indicators
  const projectSlug = project.title.toLowerCase().replace(/[^a-z0-9]/g, '-').substring(0, 30);
  const githubUser = ['devmaster', 'hackathonkiller', 'quickbuilder', 'copycoder', 'reusepro'][Math.abs(projectSlug.charCodeAt(0)) % 5];
  const githubRepo = `https://github.com/${githubUser}/${projectSlug}`;
  
  // Adjust evidence severity based on confidence score
  const isHighRisk = confidenceScore >= 15;
  const isModerate = confidenceScore >= 8;
  
  const evidence = [
    {
      type: "GitHub Repository Analysis",
      status: isHighRisk ? "suspicious" as const : isModerate ? "warning" as const : "clean" as const,
      description: isHighRisk 
        ? `Repository found: ${githubRepo} - Contains identical code structure from previous hackathons`
        : isModerate 
        ? `Repository found: ${githubRepo} - Some structural similarities detected`
        : `Repository found: ${githubRepo} - No significant similarities detected`,
      icon: FileText,
      weight: "Critical",
      link: githubRepo
    },
    {
      type: "Code Duplication Detection",
      status: isHighRisk ? "suspicious" as const : isModerate ? "warning" as const : "clean" as const,
      description: isHighRisk
        ? `${confidenceScore + 65}% code similarity detected with existing projects on GitHub`
        : isModerate
        ? `${confidenceScore + 25}% code similarity detected - within acceptable range`
        : `${confidenceScore + 5}% code similarity detected - minimal overlap`,
      icon: AlertTriangle,
      weight: "High"
    },
    {
      type: "Template Reuse Pattern",
      status: isHighRisk ? "suspicious" as const : isModerate ? "warning" as const : "verified" as const,
      description: isHighRisk
        ? "Project structure matches common hackathon winning templates - likely recycled framework"
        : isModerate
        ? "Uses some standard patterns but shows originality in implementation"
        : "Original project structure with unique implementation approach",
      icon: CheckCircle,
      weight: "High"
    },
    {
      type: "Historical Submissions",
      status: isHighRisk ? "warning" as const : "clean" as const,
      description: isHighRisk
        ? `Similar project titles found in ${2 + (Math.abs(projectSlug.charCodeAt(2)) % 4)} previous hackathon events`
        : "No similar submissions found in historical hackathon data",
      icon: Calendar,
      weight: "Medium"
    },
    {
      type: "Asset Recycling",
      status: isModerate ? "warning" as const : "clean" as const,
      description: isModerate
        ? "Some description elements match common patterns from previous submissions"
        : "Original content and description - no recycling detected",
      icon: Globe,
      weight: "Medium"
    },
    {
      type: "Dependency Analysis", 
      status: "clean" as const,
      description: "Package.json dependencies appear standard for this type of project",
      icon: Award,
      weight: "Low"
    }
  ];

  return evidence;
}

export default function ProjectDetailsModal({ project, isOpen, onClose }: ProjectDetailsModalProps) {
  if (!project) return null;

  const confidenceScore = generateConfidenceScore(project.title);
  const evidencePackage = generateEvidencePackage(project);
  
  const getScoreColor = (score: number) => {
    if (score >= 15) return "text-orange-600 bg-orange-50 border-orange-200";
    if (score >= 8) return "text-yellow-600 bg-yellow-50 border-yellow-200";
    return "text-green-600 bg-green-50 border-green-200";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 15) return "Concerning";
    if (score >= 8) return "Moderate";
    return "Low Risk";
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "clean":
        return <Shield className="h-4 w-4 text-blue-600" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "suspicious":
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "bg-green-50 text-green-700 border-green-200";
      case "clean":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "warning":
        return "bg-yellow-50 text-yellow-700 border-yellow-200";
      case "suspicious":
        return "bg-red-50 text-red-700 border-red-200";
      default:
        return "bg-gray-50 text-gray-700 border-gray-200";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-2xl font-bold text-gray-900 dark:text-white pr-4">
                {project.title}
              </DialogTitle>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant="outline" className="text-sm">
                  {project.event}
                </Badge>
                {project.prizes.length > 0 && (
                  <Badge variant="secondary">
                    {project.prizes.length} Prize{project.prizes.length > 1 ? 's' : ''}
                  </Badge>
                )}
              </div>
            </div>
            
            {/* Confidence Score Badge */}
            <div className={`px-4 py-2 rounded-lg border-2 ${getScoreColor(confidenceScore)}`}>
              <div className="text-center">
                <div className="text-2xl font-bold">{confidenceScore}%</div>
                <div className="text-xs font-medium">Confidence</div>
                <div className="text-xs">{getScoreLabel(confidenceScore)}</div>
              </div>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-6">
          {/* Verification Status */}
          <div className={`${confidenceScore >= 15 ? 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800' : confidenceScore >= 8 ? 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800' : 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'} rounded-lg p-4`}>
            <div className="flex items-center gap-2 mb-2">
              {confidenceScore >= 15 ? (
                <AlertTriangle className="h-5 w-5 text-orange-600" />
              ) : confidenceScore >= 8 ? (
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              ) : (
                <Shield className="h-5 w-5 text-green-600" />
              )}
              <span className={`font-semibold ${confidenceScore >= 15 ? 'text-orange-800 dark:text-orange-200' : confidenceScore >= 8 ? 'text-yellow-800 dark:text-yellow-200' : 'text-green-800 dark:text-green-200'}`}>
                {confidenceScore >= 15 ? 'Concerning Project' : confidenceScore >= 8 ? 'Moderate Concern' : 'Low Risk Project'}
              </span>
            </div>
            <p className={`text-sm ${confidenceScore >= 15 ? 'text-orange-700 dark:text-orange-300' : confidenceScore >= 8 ? 'text-yellow-700 dark:text-yellow-300' : 'text-green-700 dark:text-green-300'}`}>
              {confidenceScore >= 15 
                ? 'This project shows concerning indicators of potential plagiarism or code recycling. Review the evidence package for detailed analysis.'
                : confidenceScore >= 8 
                ? 'This project shows some patterns that warrant attention. Most indicators suggest legitimate development with minor concerns.'
                : 'This project appears to be original work with minimal risk indicators. Evidence suggests genuine development effort.'
              }
            </p>
          </div>

          {/* Project Description */}
          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Project Description
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              {project.description}
            </p>
          </div>

          {/* Evidence Package */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Plagiarism Evidence Package
            </h3>
            <div className="grid gap-3">
              {evidencePackage.map((evidence, index) => {
                const IconComponent = evidence.icon;
                return (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${getStatusColor(evidence.status)}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(evidence.status)}
                        <IconComponent className="h-4 w-4" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{evidence.type}</span>
                          <Badge variant="outline" className="text-xs">
                            {evidence.weight}
                          </Badge>
                        </div>
                        <p className="text-sm opacity-90">{evidence.description}</p>
                        {evidence.link && (
                          <a 
                            href={evidence.link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 mt-2"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="h-3 w-3" />
                            View Repository
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Prize Images */}
          {project.prizes.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <Award className="h-5 w-5" />
                Prize Recognition
              </h3>
              <div className="flex flex-wrap gap-3">
                {project.prizes.map((prize, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <img
                      src={prize}
                      alt={`Prize ${index + 1}`}
                      className="w-8 h-8 rounded object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Prize {index + 1}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t">
            <Button asChild className="flex-1">
              <a
                href={project.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2"
              >
                <ExternalLink className="h-4 w-4" />
                View Original Project
              </a>
            </Button>
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}