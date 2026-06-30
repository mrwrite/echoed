import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  Artifact,
  ArtifactCreateRequest,
  GenerationRun,
  KnowledgeSource,
  KnowledgeSourceCreateRequest,
  Product,
  ProductCreateRequest,
  Project,
  ProjectCreateRequest,
  Workspace,
} from '../models/v2-platform.model';

@Injectable({
  providedIn: 'root'
})
export class V2PlatformService {
  private readonly apiUrl = `${environment.apiUrl}/api`;

  constructor(private readonly http: HttpClient) {}

  getWorkspaces(): Observable<Workspace[]> {
    return this.http.get<Workspace[]>(`${this.apiUrl}/workspaces`);
  }

  getProjects(workspaceId?: string): Observable<Project[]> {
    const params = workspaceId ? new HttpParams().set('workspace_id', workspaceId) : undefined;
    return this.http.get<Project[]>(`${this.apiUrl}/projects`, { params });
  }

  getProject(projectId: string): Observable<Project> {
    return this.http.get<Project>(`${this.apiUrl}/projects/${projectId}`);
  }

  createProject(payload: ProjectCreateRequest): Observable<Project> {
    return this.http.post<Project>(`${this.apiUrl}/projects`, payload);
  }

  getProducts(filters: { workspaceId?: string; projectId?: string } = {}): Observable<Product[]> {
    let params = new HttpParams();
    if (filters.workspaceId) {
      params = params.set('workspace_id', filters.workspaceId);
    }
    if (filters.projectId) {
      params = params.set('project_id', filters.projectId);
    }
    return this.http.get<Product[]>(`${this.apiUrl}/products`, { params });
  }

  getProduct(productId: string): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}/products/${productId}`);
  }

  createProduct(payload: ProductCreateRequest): Observable<Product> {
    return this.http.post<Product>(`${this.apiUrl}/products`, payload);
  }

  getKnowledgeSources(projectId?: string): Observable<KnowledgeSource[]> {
    const params = projectId ? new HttpParams().set('project_id', projectId) : undefined;
    return this.http.get<KnowledgeSource[]>(`${this.apiUrl}/knowledge-sources`, { params });
  }

  getProjectKnowledgeSources(projectId: string): Observable<KnowledgeSource[]> {
    return this.http.get<KnowledgeSource[]>(`${this.apiUrl}/projects/${projectId}/knowledge-sources`);
  }

  createKnowledgeSource(payload: KnowledgeSourceCreateRequest): Observable<KnowledgeSource> {
    return this.http.post<KnowledgeSource>(`${this.apiUrl}/knowledge-sources`, payload);
  }

  getArtifacts(projectId?: string): Observable<Artifact[]> {
    const params = projectId ? new HttpParams().set('project_id', projectId) : undefined;
    return this.http.get<Artifact[]>(`${this.apiUrl}/artifacts`, { params });
  }

  getProjectArtifacts(projectId: string): Observable<Artifact[]> {
    return this.http.get<Artifact[]>(`${this.apiUrl}/projects/${projectId}/artifacts`);
  }

  getArtifact(artifactId: string): Observable<Artifact> {
    return this.http.get<Artifact>(`${this.apiUrl}/artifacts/${artifactId}`);
  }

  createArtifact(payload: ArtifactCreateRequest): Observable<Artifact> {
    return this.http.post<Artifact>(`${this.apiUrl}/artifacts`, payload);
  }

  getGenerationRuns(projectId?: string): Observable<GenerationRun[]> {
    const params = projectId ? new HttpParams().set('project_id', projectId) : undefined;
    return this.http.get<GenerationRun[]>(`${this.apiUrl}/generation-runs`, { params });
  }

  getProjectGenerationRuns(projectId: string): Observable<GenerationRun[]> {
    return this.http.get<GenerationRun[]>(`${this.apiUrl}/projects/${projectId}/generation-runs`);
  }

  getGenerationRun(generationRunId: string): Observable<GenerationRun> {
    return this.http.get<GenerationRun>(`${this.apiUrl}/generation-runs/${generationRunId}`);
  }
}
