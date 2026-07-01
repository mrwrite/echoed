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

  it('loads public product pages without workspace filters', () => {
    service.getPublicProducts().subscribe(products => {
      expect(products[0].slug).toBe('course-product');
    });
    service.getPublicProduct('course-product').subscribe(product => {
      expect(product.title).toBe('Course Product');
    });

    const listRequest = httpMock.expectOne(`${environment.apiUrl}/api/public/products`);
    expect(listRequest.request.method).toBe('GET');
    listRequest.flush([
      {
        id: 'product-1',
        workspace_id: 'workspace-1',
        project_id: null,
        course_id: null,
        program_id: null,
        product_type: 'course',
        title: 'Course Product',
        slug: 'course-product',
        description: null,
        status: 'published',
        review_state: 'approved',
        access_state: 'private',
        visibility: 'public',
        pricing_model: 'free',
        certificate_available: false,
        featured: false,
        metadata: {},
        published_at: '2026-01-01T00:00:00',
        created_at: '2026-01-01T00:00:00',
        updated_at: '2026-01-01T00:00:00',
      },
    ]);

    const detailRequest = httpMock.expectOne(`${environment.apiUrl}/api/public/products/course-product`);
    expect(detailRequest.request.method).toBe('GET');
    detailRequest.flush({
      id: 'product-1',
      workspace_id: 'workspace-1',
      project_id: null,
      course_id: null,
      program_id: null,
      product_type: 'course',
      title: 'Course Product',
      slug: 'course-product',
      description: null,
      status: 'published',
      review_state: 'approved',
      access_state: 'private',
      visibility: 'public',
      pricing_model: 'free',
      certificate_available: false,
      featured: false,
      metadata: {},
      published_at: '2026-01-01T00:00:00',
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });
  });

  it('publishes product wrappers without checkout execution', () => {
    service.publishProduct('product-1', { visibility: 'public' }).subscribe(product => {
      expect(product.status).toBe('published');
      expect(product.visibility).toBe('public');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/products/product-1/publish`);
    expect(request.request.method).toBe('PATCH');
    expect(request.request.body.visibility).toBe('public');
    request.flush({
      id: 'product-1',
      workspace_id: 'workspace-1',
      project_id: null,
      course_id: null,
      program_id: null,
      product_type: 'course',
      title: 'Course Product',
      slug: 'course-product',
      description: null,
      status: 'published',
      review_state: 'approved',
      access_state: 'private',
      visibility: 'public',
      pricing_model: 'free',
      certificate_available: false,
      featured: false,
      metadata: {},
      published_at: '2026-01-01T00:00:00',
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

  it('loads the Review Center aggregate queue', () => {
    service.getReviewCenter().subscribe(center => {
      expect(center.pending_artifacts[0].title).toBe('Pending Artifact');
      expect(center.draft_products[0].status).toBe('draft');
      expect(center.lesson_governance_items[0].blocked).toBeTrue();
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/review-center`);
    expect(request.request.method).toBe('GET');
    request.flush({
      pending_artifacts: [
        {
          id: 'artifact-1',
          item_type: 'artifact',
          title: 'Pending Artifact',
          status: 'in_review',
          review_state: 'in_review',
          owner: null,
          source_coverage: 'Linked knowledge source',
          readiness: 'Wrapper review only; not learner-deliverable',
          required_decision: 'Review artifact wrapper',
          blocked: false,
          detail_route: '/workspace/artifacts/artifact-1',
          governance_route: null,
          updated_at: '2026-01-01T00:00:00',
        },
      ],
      draft_products: [
        {
          id: 'product-1',
          item_type: 'product',
          title: 'Draft Product',
          status: 'draft',
          review_state: 'not_reviewed',
          owner: null,
          source_coverage: 'Course-backed runtime link',
          readiness: 'Existing lesson governance remains authoritative',
          required_decision: 'Review product wrapper',
          blocked: false,
          detail_route: '/workspace/products/product-1',
          governance_route: '/workspace/product-studio/courses/course-1/edit',
          updated_at: '2026-01-01T00:00:00',
        },
      ],
      lesson_governance_items: [
        {
          id: 'course-1',
          item_type: 'lesson_governance',
          title: 'Blocked Course',
          status: 'blocked',
          review_state: 'existing_governance',
          owner: null,
          source_coverage: '1 blocking issue(s), 0 warning(s)',
          readiness: 'Blocked',
          required_decision: 'Resolve lesson governance blockers',
          blocked: true,
          detail_route: '/workspace/product-studio/courses/course-1/edit',
          governance_route: '/workspace/product-studio/courses/course-1/edit',
          updated_at: '2026-01-01T00:00:00',
        },
      ],
      recent_activity: [
        {
          id: 'review-activity-placeholder',
          message: 'Review activity history will appear here after audit records are introduced.',
          created_at: null,
        },
      ],
    });
  });

  it('updates artifact review status through the wrapper API', () => {
    service.updateArtifactReviewStatus('artifact-1', { status: 'approved' }).subscribe(artifact => {
      expect(artifact.status).toBe('approved');
      expect(artifact.review_state).toBe('approved');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/artifacts/artifact-1/review-status`);
    expect(request.request.method).toBe('PATCH');
    expect(request.request.body.status).toBe('approved');
    request.flush({
      id: 'artifact-1',
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      product_id: null,
      generation_run_id: null,
      knowledge_source_id: null,
      artifact_type: 'guide',
      title: 'Artifact',
      body: null,
      uri: null,
      status: 'approved',
      review_state: 'approved',
      metadata: {},
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });
  });

  it('updates product review status through the wrapper API', () => {
    service.updateProductReviewStatus('product-1', { status: 'approved' }).subscribe(product => {
      expect(product.status).toBe('approved');
      expect(product.review_state).toBe('approved');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/products/product-1/review-status`);
    expect(request.request.method).toBe('PATCH');
    expect(request.request.body.status).toBe('approved');
    request.flush({
      id: 'product-1',
      workspace_id: 'workspace-1',
      project_id: 'project-1',
      course_id: 'course-1',
      program_id: null,
      product_type: 'course',
      title: 'Product',
      description: null,
      status: 'approved',
      review_state: 'approved',
      access_state: 'private',
      metadata: {},
      published_at: null,
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });
  });

  it('loads learner portal products from the V2 learner API', () => {
    service.getLearnerProducts().subscribe(products => {
      expect(products.length).toBe(2);
      expect(products[0].is_enrolled).toBeTrue();
      expect(products[1].product_status).toBe('approved');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/learner-portal/products`);
    expect(request.request.method).toBe('GET');
    request.flush([
      {
        id: 'product-1',
        product_id: 'product-1',
        course_id: 'course-1',
        title: 'Enrolled Product',
        description: 'Existing runtime enrollment',
        product_type: 'course',
        product_status: 'draft',
        review_state: 'draft',
        access_state: 'private',
        enrollment_id: 'student-course-1',
        enrollment_status: 'active',
        enrolled_on: '2026-01-01T00:00:00',
        is_enrolled: true,
        source: 'product_wrapper',
        learner_visibility: 'Existing enrollment controls access; lesson governance controls content.',
        next_action: 'Continue governed course runtime',
      },
      {
        id: 'product-2',
        product_id: 'product-2',
        course_id: 'course-2',
        title: 'Available Product',
        description: 'Approved wrapper',
        product_type: 'course',
        product_status: 'approved',
        review_state: 'approved',
        access_state: 'private',
        enrollment_id: null,
        enrollment_status: null,
        enrolled_on: null,
        is_enrolled: false,
        source: 'product_wrapper',
        learner_visibility: 'Available wrapper; enrollment still uses existing course runtime.',
        next_action: 'Enroll through existing course enrollment',
      },
    ]);
  });

  it('manages access grants through the V2 access API', () => {
    service.getAccessGrants({ productId: 'product-1' }).subscribe(grants => {
      expect(grants[0].grant_type).toBe('manual');
    });
    const listRequest = httpMock.expectOne(`${environment.apiUrl}/api/access-grants?product_id=product-1`);
    expect(listRequest.request.method).toBe('GET');
    listRequest.flush([
      {
        id: 'grant-1',
        user_id: 'user-1',
        product_id: 'product-1',
        workspace_id: 'workspace-1',
        project_id: null,
        grant_type: 'manual',
        status: 'active',
        source: 'manual',
        starts_at: null,
        expires_at: null,
        revoked_at: null,
        metadata: {},
        created_at: '2026-01-01T00:00:00',
        updated_at: '2026-01-01T00:00:00',
      },
    ]);

    service.createAccessGrant({
      user_id: 'user-1',
      product_id: 'product-1',
      grant_type: 'manual',
    }).subscribe(grant => {
      expect(grant.status).toBe('active');
    });
    const createRequest = httpMock.expectOne(`${environment.apiUrl}/api/access-grants`);
    expect(createRequest.request.method).toBe('POST');
    expect(createRequest.request.body.user_id).toBe('user-1');
    createRequest.flush({
      id: 'grant-1',
      user_id: 'user-1',
      product_id: 'product-1',
      workspace_id: 'workspace-1',
      project_id: null,
      grant_type: 'manual',
      status: 'active',
      source: 'manual',
      starts_at: null,
      expires_at: null,
      revoked_at: null,
      metadata: {},
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-01T00:00:00',
    });

    service.revokeAccessGrant('grant-1').subscribe(grant => {
      expect(grant.status).toBe('revoked');
    });
    const revokeRequest = httpMock.expectOne(`${environment.apiUrl}/api/access-grants/grant-1/revoke`);
    expect(revokeRequest.request.method).toBe('PATCH');
    revokeRequest.flush({
      id: 'grant-1',
      user_id: 'user-1',
      product_id: 'product-1',
      workspace_id: 'workspace-1',
      project_id: null,
      grant_type: 'manual',
      status: 'revoked',
      source: 'manual',
      starts_at: null,
      expires_at: null,
      revoked_at: '2026-01-02T00:00:00',
      metadata: {},
      created_at: '2026-01-01T00:00:00',
      updated_at: '2026-01-02T00:00:00',
    });
  });
});
