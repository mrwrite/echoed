import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../environments/environment';
import { V2PlatformService } from './v2-platform.service';

describe('V2PlatformService', () => {
  let service: V2PlatformService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(V2PlatformService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('lists products from the V2 product API', () => {
    service.getProducts({ workspaceId: 'workspace-1' }).subscribe(products => {
      expect(products.length).toBe(1);
      expect(products[0].course_id).toBe('course-1');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/products?workspace_id=workspace-1`);
    expect(request.request.method).toBe('GET');
    request.flush([
      {
        id: 'product-1',
        workspace_id: 'workspace-1',
        project_id: null,
        course_id: 'course-1',
        program_id: null,
        product_type: 'course',
        title: 'Course Product',
        description: 'Course-backed',
        status: 'active',
        review_state: 'runtime_authoritative',
        access_state: 'existing_runtime',
        metadata: {},
        published_at: null,
        created_at: '2026-01-01T00:00:00',
        updated_at: '2026-01-01T00:00:00',
      },
    ]);
  });

  it('creates project shells through the V2 project API', () => {
    service.createProject({
      workspace_id: 'workspace-1',
      name: 'Project Shell',
      description: 'Additive project',
    }).subscribe(project => {
      expect(project.name).toBe('Project Shell');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/projects`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body.workspace_id).toBe('workspace-1');
    request.flush({
      id: 'project-1',
      workspace_id: 'workspace-1',
      name: 'Project Shell',
      description: 'Additive project',
      status: 'active',
      metadata: {},
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });
  });

  it('creates product shells through the V2 product API', () => {
    service.createProduct({
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      course_id: 'course-1',
      product_type: 'course',
      title: 'Course Product',
    }).subscribe(product => {
      expect(product.title).toBe('Course Product');
      expect(product.course_id).toBe('course-1');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/products`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body.course_id).toBe('course-1');
    request.flush({
      id: 'product-1',
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      course_id: 'course-1',
      program_id: null,
      product_type: 'course',
      title: 'Course Product',
      description: null,
      status: 'draft',
      review_state: 'runtime_authoritative',
      access_state: 'existing_runtime',
      metadata: {},
      published_at: null,
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });
  });

  it('creates knowledge source shells through the V2 source API', () => {
    service.createKnowledgeSource({
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      title: 'Repository Source',
      source_type: 'repository',
      uri: 'https://example.com/repo',
    }).subscribe(source => {
      expect(source.title).toBe('Repository Source');
      expect(source.project_id).toBe('project-1');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/knowledge-sources`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body.source_type).toBe('repository');
    request.flush({
      id: 'source-1',
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      source_id: null,
      title: 'Repository Source',
      source_type: 'repository',
      uri: 'https://example.com/repo',
      citation: null,
      content_hash: null,
      status: 'available',
      metadata: {},
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });
  });

  it('creates artifact shells through the V2 artifact API', () => {
    service.createArtifact({
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      product_id: 'product-1',
      knowledge_source_id: 'source-1',
      artifact_type: 'guide',
      title: 'Implementation Guide',
      body: 'Reviewable draft',
    }).subscribe(artifact => {
      expect(artifact.title).toBe('Implementation Guide');
      expect(artifact.review_state).toBe('review_required');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/artifacts`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body.knowledge_source_id).toBe('source-1');
    request.flush({
      id: 'artifact-1',
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      product_id: 'product-1',
      generation_run_id: null,
      knowledge_source_id: 'source-1',
      artifact_type: 'guide',
      title: 'Implementation Guide',
      body: 'Reviewable draft',
      uri: null,
      status: 'draft',
      review_state: 'review_required',
      metadata: {},
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });
  });

  it('reads project-scoped pipeline collections', () => {
    service.getProjectKnowledgeSources('project-1').subscribe(sources => {
      expect(sources.length).toBe(0);
    });
    const request = httpMock.expectOne(`${environment.apiUrl}/api/projects/project-1/knowledge-sources`);
    expect(request.request.method).toBe('GET');
    request.flush([]);
  });
});
