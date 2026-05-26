describe('Global accessibility focus styles', () => {
  it('does not globally suppress visible focus affordances on interactive controls', () => {
    const button = document.createElement('button');
    button.textContent = 'Focusable control';
    document.body.appendChild(button);

    button.focus();
    const computed = getComputedStyle(button);

    expect(computed.outlineStyle).not.toBe('none');

    document.body.removeChild(button);
  });
});
