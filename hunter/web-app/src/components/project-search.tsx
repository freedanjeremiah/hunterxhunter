"use client";

import { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Search, ExternalLink, Loader2 } from "lucide-react";
import ProjectDetailsModal from "./project-details-modal";

interface Project {
  title: string;
  description: string;
  event: string;
  url: string;
  prizes: string[];
}

interface ProjectsData {
  projects: Project[];
}

// Custom hook for debouncing
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Loading skeleton component
function ProjectSkeleton() {
  return (
    <Card className="h-full">
      <CardHeader>
        <div className="space-y-2">
          <div className="h-6 bg-gray-200 rounded-md animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded-md w-2/3 animate-pulse"></div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded-md animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded-md animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded-md w-1/2 animate-pulse"></div>
          <div className="h-10 bg-gray-200 rounded-md animate-pulse mt-4"></div>
        </div>
      </CardContent>
    </Card>
  );
}

const ITEMS_PER_PAGE = 12;
const CACHE_KEY = "projects-cache";
const CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

export default function ProjectSearch() {
  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [displayedProjects, setDisplayedProjects] = useState<Project[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMorePages, setHasMorePages] = useState(true);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Cache management
  const getCachedProjects = (): { data: Project[], timestamp: number } | null => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < CACHE_EXPIRY) {
          return { data, timestamp };
        }
      }
    } catch (error) {
      console.warn("Failed to load cached data:", error);
    }
    return null;
  };

  const setCachedProjects = (projects: Project[]) => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({
        data: projects,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.warn("Failed to cache data:", error);
    }
  };

  // Load projects data with caching
  useEffect(() => {
    const loadProjects = async () => {
      try {
        // Check cache first
        const cached = getCachedProjects();
        if (cached) {
          setAllProjects(cached.data);
          setIsLoading(false);
          return;
        }

        // Cancel any existing request
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }

        abortControllerRef.current = new AbortController();

        const response = await fetch("/projects.json", {
          signal: abortControllerRef.current.signal
        });
        
        if (!response.ok) {
          throw new Error("Failed to load projects data");
        }
        
        const data: ProjectsData = await response.json();
        setAllProjects(data.projects);
        setCachedProjects(data.projects);
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setError(err.message);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadProjects();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Filter and paginate projects
  const filteredProjects = useMemo(() => {
    if (!debouncedSearchTerm.trim()) {
      return allProjects;
    }

    const term = debouncedSearchTerm.toLowerCase();
    return allProjects.filter(
      (project) =>
        project.title.toLowerCase().includes(term) ||
        project.description.toLowerCase().includes(term) ||
        project.event.toLowerCase().includes(term)
    );
  }, [allProjects, debouncedSearchTerm]);

  // Update displayed projects when filtered projects or page changes
  useEffect(() => {
    const startIndex = 0;
    const endIndex = currentPage * ITEMS_PER_PAGE;
    const newDisplayedProjects = filteredProjects.slice(startIndex, endIndex);
    
    setDisplayedProjects(newDisplayedProjects);
    setHasMorePages(endIndex < filteredProjects.length);
  }, [filteredProjects, currentPage]);

  // Reset pagination when search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearchTerm]);

  // Load more projects
  const loadMore = useCallback(() => {
    if (!isLoadingMore && hasMorePages) {
      setIsLoadingMore(true);
      setTimeout(() => {
        setCurrentPage(prev => prev + 1);
        setIsLoadingMore(false);
      }, 300); // Small delay to show loading state
    }
    }, [isLoadingMore, hasMorePages]);

  // Handle project card click
  const handleProjectClick = useCallback((project: Project) => {
    setSelectedProject(project);
    setIsModalOpen(true);
  }, []);

  // Handle modal close
  const handleModalClose = useCallback(() => {
    setIsModalOpen(false);
    setSelectedProject(null);
  }, []);  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        {/* Top Corner Buttons */}
        <div className="fixed top-4 left-0 right-0 z-50 px-4">
          <div className="flex justify-between items-center max-w-7xl mx-auto">
            <Button 
              variant="outline" 
              size="sm"
              className="bg-white/90 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Menu
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className="bg-white/90 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Git Walrus
            </Button>
          </div>
        </div>

        <div className="text-center mb-8 mt-16">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Project Explorer
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            Discover amazing projects from hackathons and events
          </p>
          
          <div className="relative max-w-md mx-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              type="text"
              placeholder="Search projects by title, description, or event..."
              value=""
              className="pl-10 pr-4 py-2"
              disabled
            />
          </div>
        </div>

        {/* Loading skeletons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, index) => (
            <ProjectSkeleton key={index} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        {/* Top Corner Buttons */}
        <div className="fixed top-4 left-0 right-0 z-50 px-4">
          <div className="flex justify-between items-center max-w-7xl mx-auto">
            <Button 
              variant="outline" 
              size="sm"
              className="bg-white/90 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Menu
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className="bg-white/90 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Git Walrus
            </Button>
          </div>
        </div>

        <div className="text-center text-red-600 mt-16">
          <p>Error: {error}</p>
          <Button 
            onClick={() => window.location.reload()} 
            variant="outline" 
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Top Corner Buttons */}
      <div className="fixed top-4 left-0 right-0 z-50 px-4">
        <div className="flex justify-between items-center max-w-7xl mx-auto">
          <Button 
            variant="outline" 
            size="sm"
            className="bg-white/90 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Menu
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            className="bg-white/90 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Git Walrus
          </Button>
        </div>
      </div>

      {/* Header and Search */}
      <div className="text-center mb-8 mt-16">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Project Explorer
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
          Discover amazing projects from hackathons and events
        </p>
        
        {/* Search Bar */}
        <div className="relative max-w-md mx-auto">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search projects by title, description, or event..."
            value={searchTerm || ""}
            onChange={(e) => setSearchTerm(e.target.value || "")}
            className="pl-10 pr-4 py-2"
          />
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-6">
        <p className="text-gray-600 dark:text-gray-300">
          {debouncedSearchTerm ? (
            <>Showing {displayedProjects.length} of {filteredProjects.length} results for "{debouncedSearchTerm}"</>
          ) : (
            <>Showing {displayedProjects.length} of {allProjects.length} projects</>
          )}
        </p>
      </div>

      {/* Projects Grid */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 text-lg">
            No projects found matching your search criteria.
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayedProjects.map((project, index) => (
              <Card 
                key={index} 
                className="h-full hover:shadow-lg transition-all duration-200 cursor-pointer hover:scale-[1.02]"
                onClick={() => handleProjectClick(project)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start gap-2">
                    <CardTitle className="text-lg font-semibold line-clamp-2">
                      {project.title}
                    </CardTitle>
                    {project.prizes.length > 0 && (
                      <Badge variant="secondary" className="shrink-0">
                        {project.prizes.length} Prize{project.prizes.length > 1 ? 's' : ''}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {project.event}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3 mb-4">
                    {project.description}
                  </CardDescription>
                  
                  {/* Prize Images */}
                  {project.prizes.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {project.prizes.slice(0, 3).map((prize, prizeIndex) => (
                        <img
                          key={prizeIndex}
                          src={prize}
                          alt={`Prize ${prizeIndex + 1}`}
                          className="w-6 h-6 rounded object-cover"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      ))}
                    </div>
                  )}
                  
                  <div className="flex gap-2">
                    <Button 
                      asChild 
                      className="flex-1" 
                      variant="outline"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <a
                        href={project.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center gap-2"
                      >
                        <ExternalLink className="h-4 w-4" />
                        View Project
                      </a>
                    </Button>
                    <Button 
                      size="sm" 
                      variant="secondary"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleProjectClick(project);
                      }}
                    >
                      Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Project Details Modal */}
          <ProjectDetailsModal 
            project={selectedProject}
            isOpen={isModalOpen}
            onClose={handleModalClose}
          />

          {/* Load More Button */}
          {hasMorePages && (
            <div className="text-center mt-8">
              <Button
                onClick={loadMore}
                variant="outline"
                className="px-8"
                disabled={isLoadingMore}
              >
                {isLoadingMore ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Loading...
                  </>
                ) : (
                  'Load More Projects'
                )}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}